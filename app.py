# app.py (version-c branch)
import os
import sys
import requests
import json
from flask import Flask, request, jsonify
from web3 import Web3
from src.config import w3, CONTRACT_ADDRESS_C, OWNER_ADDRESS, OWNER_PRIVATE_KEY

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "EricTylerZ/StagQuest"

CONTRACTS = {
    "c": {"address": CONTRACT_ADDRESS_C, "status_file": "data/stag_status_c.json"}
}

ABI_URL = "https://raw.githubusercontent.com/EricTylerZ/StagQuest/version-c/data/abi.json"  # Updated to abi.json

def load_json_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to load {url}: Status {response.status_code}")

try:
    abi = load_json_from_url(ABI_URL)
    contracts = {"c": w3.eth.contract(address=CONTRACT_ADDRESS_C, abi=abi)}
except Exception as e:
    app.logger.error(f"Failed to load ABI: {e}")
    contracts = {"c": None}

def update_github_file(content, version="c"):
    if not GITHUB_TOKEN:
        app.logger.error("GITHUB_TOKEN not set")
        return False
    
    file_path = CONTRACTS[version]["status_file"]
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    get_response = requests.get(api_url, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None
    
    payload = {"message": f"Update {file_path}", "content": "", "branch": "version-c"}
    if sha:
        payload["sha"] = sha
    
    import base64
    payload["content"] = base64.b64encode(json.dumps(content, indent=2).encode()).decode()
    
    response = requests.put(api_url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        app.logger.info(f"Successfully updated {file_path}: {response.status_code}")
        return True
    else:
        app.logger.error(f"Failed to update {file_path}: {response.status_code} - {response.text}")
        return False

def get_contract(version="c"):
    version = version.lower()
    if version not in CONTRACTS:
        return None, "Invalid version (use 'c')"
    contract = contracts.get(version)
    if not contract:
        return None, "Contract not initialized"
    return contract, None

@app.route("/api/mint", methods=["POST"])
def mint():
    version = request.args.get("version", "c").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    try:
        data = request.get_json() or {}
        amount = data.get("amount", "0.0001")  # Default to min
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.mintStag().build_transaction({
            "from": OWNER_ADDRESS,
            "value": w3.to_wei(amount, "ether"),
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            token_id = None
            for log in receipt["logs"]:
                if log["topics"][0].hex() == w3.keccak(text="Transfer(address,address,uint256)").hex():
                    token_id = int(log["topics"][3].hex(), 16)
                    break
            if token_id:
                update_github_file(get_status_data(contract), version)
                return jsonify({"message": "Stag minted", "tokenId": token_id, "txHash": tx_hash.hex()}), 200
            return jsonify({"error": "Mint succeeded but no tokenId found", "txHash": tx_hash.hex()}), 500
        return jsonify({"error": "Minting failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Mint failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/novena", methods=["POST"])
def start_novena():
    version = request.args.get("version", "c").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json()
    stag_id = data.get("stagId")
    amount = data.get("amount", "0")  # Optional ETH
    if not stag_id or not isinstance(stag_id, int):
        return jsonify({"error": "Invalid or missing stagId"}), 400
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.startNovena(stag_id).build_transaction({
            "from": OWNER_ADDRESS,
            "value": w3.to_wei(amount, "ether"),
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data(contract), version)
            return jsonify({"message": f"Novena started for stagId {stag_id}", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Novena start failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Novena start failed for stagId {stag_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/complete-novena", methods=["POST"])
def complete_novena():
    version = request.args.get("version", "c").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json()
    stag_id = data.get("stagId")
    successful_days = data.get("successfulDays", 0)
    if not stag_id or not isinstance(stag_id, int) or not isinstance(successful_days, int) or successful_days > 9:
        return jsonify({"error": "Invalid stagId or successfulDays (0-9)"}), 400
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        txn = contract.functions.completeNovena(stag_id, successful_days).build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_txn = w3.eth.account.sign_transaction(txn, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data(contract), version)
            return jsonify({"stagId": stag_id, "successfulDays": successful_days, "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Completion failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Completion failed for stagId {stag_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/batch-complete-novena", methods=["POST"])
def batch_complete_novena():
    version = request.args.get("version", "c").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json()
    stag_ids = data.get("stagIds", [])
    successes = data.get("successfulDays", [])
    if not stag_ids or not isinstance(stag_ids, list) or len(stag_ids) != len(successes):
        return jsonify({"error": "Invalid stagIds or successfulDays array"}), 400
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        txn = contract.functions.batchCompleteNovena(stag_ids, successes).build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_txn = w3.eth.account.sign_transaction(txn, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data(contract), version)
            return jsonify({"message": "Batch completion successful", "stagIds": stag_ids, "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Batch completion failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Batch completion failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/transfer", methods=["POST"])
def transfer():
    version = request.args.get("version", "c").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json()
    stag_id = data.get("stagId")
    to_address = data.get("toAddress")
    if not stag_id or not isinstance(stag_id, int) or not Web3.is_address(to_address):
        return jsonify({"error": "Invalid stagId or toAddress"}), 400
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.transferFrom(OWNER_ADDRESS, to_address, stag_id).build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 100000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data(contract), version)
            return jsonify({"message": f"Stag {stag_id} transferred to {to_address}", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Transfer failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Transfer failed for stagId {stag_id}: {e}")
        return jsonify({"error": str(e)}), 500

def get_status_data(contract):
    try:
        total_supply = contract.functions.totalSupply().call()
        next_token_id = contract.functions.nextTokenId().call()
        stags = []
        for token_id in range(1, next_token_id):
            try:
                owner = contract.functions.ownerOf(token_id).call()
                family_size = contract.functions.familySize(token_id).call()
                has_novena = contract.functions.hasActiveNovena(token_id).call()
                successful_days = contract.functions.successfulDays(token_id).call()
                stag_data = {
                    "tokenId": token_id,
                    "owner": owner,
                    "familySize": family_size,
                    "hasActiveNovena": has_novena,
                    "successfulDays": successful_days
                }
                stags.append(stag_data)
            except Exception as e:
                app.logger.error(f"Failed to fetch status for tokenId {token_id}: {e}")
                continue
        return {"stags": stags}
    except Exception as e:
        app.logger.error(f"Status fetch failed: {e}")
        return {"stags": []}

@app.route("/api/status", methods=["GET"])
def status():
    version = request.args.get("version", "c").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    status_data = get_status_data(contract)
    return jsonify(status_data), 200

@app.route("/api/owner-withdraw", methods=["POST"])
def owner_withdraw():
    version = request.args.get("version", "c").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.withdrawOwnerFunds().build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            return jsonify({"message": "Owner funds withdrawn", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Owner withdrawal failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Owner withdrawal failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "StagQuest Owner API", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)