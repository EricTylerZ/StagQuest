# app.py
import os
import sys
import requests
from flask import Flask, request, jsonify
from web3 import Web3
from src.config import w3, CONTRACT_ADDRESS, ORACLE_ADDRESS, ORACLE_PRIVATE_KEY

app = Flask(__name__)

# Load ABI from GitHub
ABI_URL = "https://raw.githubusercontent.com/EricTylerZ/StagQuest/main/data/abi.json"

def load_json_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to load {url}: Status {response.status_code}")

try:
    abi = load_json_from_url(ABI_URL)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
except Exception as e:
    app.logger.error(f"Failed to load ABI: {e}")
    contract = None

@app.route("/api/mint", methods=["POST"])
def mint():
    if not contract:
        return jsonify({"error": "Contract not initialized"}), 500

    try:
        nonce = w3.eth.get_transaction_count(ORACLE_ADDRESS)
        mint_fee = w3.to_wei("0.0001", "ether")
        tx = contract.functions.mintStag().build_transaction({
            "from": ORACLE_ADDRESS,
            "value": mint_fee,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, ORACLE_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            token_id = None
            for log in receipt["logs"]:
                if log["topics"][0].hex() == w3.keccak(text="Transfer(address,address,uint256)").hex():
                    token_id = int(log["topics"][3].hex(), 16)
                    break
            if token_id:
                return jsonify({"message": "Stag minted", "tokenId": token_id, "txHash": tx_hash.hex()}), 200
            return jsonify({"error": "Mint succeeded but no tokenId found", "txHash": tx_hash.hex()}), 500
        else:
            return jsonify({"error": "Minting failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Mint failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/novena", methods=["POST"])
def start_novena():
    if not contract:
        return jsonify({"error": "Contract not initialized"}), 500

    data = request.get_json()
    stag_id = data.get("stagId")
    if not stag_id or not isinstance(stag_id, int):
        return jsonify({"error": "Invalid or missing stagId"}), 400

    try:
        owner = contract.functions.ownerOf(stag_id).call()
        has_novena = contract.functions.hasActiveNovena(stag_id).call()
        if has_novena:
            return jsonify({"error": f"Stag {stag_id} already has an active novena"}), 400

        nonce = w3.eth.get_transaction_count(ORACLE_ADDRESS)
        stake = w3.to_wei("0.0009", "ether")
        tx = contract.functions.startNovena(stag_id).build_transaction({
            "from": ORACLE_ADDRESS,
            "value": stake,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, ORACLE_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            return jsonify({"message": f"Novena started for stagId {stag_id}", "txHash": tx_hash.hex()}), 200
        else:
            return jsonify({"error": "Novena start failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Novena start failed for stagId {stag_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/checkin", methods=["POST"])
def checkin():
    if not contract:
        return jsonify({"error": "Contract not initialized"}), 500

    data = request.get_json()
    stag_id = data.get("stagId")
    if not stag_id or not isinstance(stag_id, int):
        return jsonify({"error": "Invalid or missing stagId"}), 400

    try:
        owner = contract.functions.ownerOf(stag_id).call()
        has_novena = contract.functions.hasActiveNovena(stag_id).call()
        if not has_novena:
            return jsonify({"error": f"No active novena for stagId {stag_id}. Start one first."}), 400

        success = True  # Replace with real logic (e.g., Twilio) later

        nonce = w3.eth.get_transaction_count(ORACLE_ADDRESS)
        txn = contract.functions.checkIn(stag_id, success).build_transaction({
            "from": ORACLE_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("20", "gwei"),
            "chainId": 84532
        })
        signed_txn = w3.eth.account.sign_transaction(txn, ORACLE_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            return jsonify({"stagId": stag_id, "success": success, "txHash": tx_hash.hex()}), 200
        else:
            return jsonify({"error": "Check-in failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Check-in failed for stagId {stag_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/status", methods=["GET"])
def status():
    if not contract:
        return jsonify({"error": "Contract not initialized"}), 500

    try:
        # Get total supply of Stags
        total_supply = contract.functions.totalSupply().call()
        stags = []

        # Loop through all token IDs (assuming they start at 1 and are sequential)
        for token_id in range(1, total_supply + 1):
            try:
                owner = contract.functions.ownerOf(token_id).call()
                family_size = contract.functions.familySize(token_id).call()
                has_novena = contract.functions.hasActiveNovena(token_id).call()
                days_completed = contract.functions.daysCompleted(token_id).call()
                successful_days = contract.functions.successfulDays(token_id).call()
                stake = contract.functions.activeStakes(token_id).call()

                stags.append({
                    "tokenId": token_id,
                    "owner": owner,
                    "familySize": family_size,
                    "hasActiveNovena": has_novena,
                    "daysCompleted": days_completed,
                    "successfulDays": successful_days,
                    "stake": w3.from_wei(stake, "ether")  # Convert to ETH for readability
                })
            except Exception as e:
                app.logger.error(f"Failed to fetch status for tokenId {token_id}: {e}")
                continue  # Skip invalid token IDs

        return jsonify({"stags": stags}), 200
    except Exception as e:
        app.logger.error(f"Status fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "StagQuest Oracle API", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)