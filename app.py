# app.py
import os
import sys
import requests
import json
from flask import Flask, request, jsonify
from web3 import Web3
from src.config import w3, CONTRACT_ADDRESS, ORACLE_ADDRESS, ORACLE_PRIVATE_KEY

app = Flask(__name__)

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "EricTylerZ/StagQuest"
GITHUB_FILE_PATH = "data/stag_status.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

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

def update_github_file(content):
    """Update stag_status.json in GitHub repo."""
    if not GITHUB_TOKEN:
        app.logger.error("GITHUB_TOKEN not set in environment variables")
        return False

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get current file SHA (if it exists)
    get_response = requests.get(GITHUB_API_URL, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None

    # Prepare update payload
    payload = {
        "message": "Update stag_status.json from /api/status",
        "content": "",
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    # Encode content to base64
    import base64
    payload["content"] = base64.b64encode(json.dumps(content, indent=2).encode()).decode()

    # Update file
    response = requests.put(GITHUB_API_URL, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        app.logger.info(f"Successfully updated stag_status.json on GitHub: {response.status_code}")
        return True
    else:
        app.logger.error(f"Failed to update GitHub: {response.status_code} - {response.text}")
        return False

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
        total_supply = contract.functions.totalSupply().call()
        next_token_id = contract.functions.nextTokenId().call()
        stags = []

        for token_id in range(1, next_token_id):
            try:
                owner = contract.functions.ownerOf(token_id).call()
                family_size = contract.functions.familySize(token_id).call()
                has_novena = contract.functions.hasActiveNovena(token_id).call()
                days_completed = contract.functions.daysCompleted(token_id).call()
                successful_days = contract.functions.successfulDays(token_id).call()
                stake = contract.functions.activeStakes(token_id).call()

                stag_data = {
                    "tokenId": token_id,
                    "owner": owner,
                    "familySize": family_size,
                    "hasActiveNovena": has_novena,
                    "daysCompleted": days_completed,
                    "successfulDays": successful_days,
                    "stake": w3.from_wei(stake, "ether")
                }
                stags.append(stag_data)
            except Exception as e:
                app.logger.error(f"Failed to fetch status for tokenId {token_id}: {e}")
                continue

        # Sync to GitHub
        sync_success = False
        if stags:
            sync_success = update_github_file({"stags": stags})

        response = {"stags": stags}
        if not sync_success:
            response["warning"] = "GitHub sync failed - status data not updated in repo"
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Status fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "StagQuest Oracle API", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)