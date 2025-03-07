# app.py (version-b branch)
import os
import sys
import requests
import json
from flask import Flask, request, jsonify
from web3 import Web3
from src.config import w3, CONTRACT_ADDRESS_A, CONTRACT_ADDRESS_B, ORACLE_ADDRESS, ORACLE_PRIVATE_KEY, OWNER_ADDRESS, OWNER_PRIVATE_KEY

app = Flask(__name__)

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "EricTylerZ/StagQuest"

# Contract versions
CONTRACTS = {
    "a": {"address": CONTRACT_ADDRESS_A, "status_file": "data/stag_status_a.json"},
    "b": {"address": CONTRACT_ADDRESS_B, "status_file": "data/stag_status_b.json"}
}

# Load ABI from GitHub
ABI_URL = "https://raw.githubusercontent.com/EricTylerZ/StagQuest/main/data/abi.json"

def load_json_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to load {url}: Status {response.status_code}")

try:
    abi = load_json_from_url(ABI_URL)
    contracts = {
        "a": w3.eth.contract(address=CONTRACT_ADDRESS_A, abi=abi),
        "b": w3.eth.contract(address=CONTRACT_ADDRESS_B, abi=abi)
    }
except Exception as e:
    app.logger.error(f"Failed to load ABI: {e}")
    contracts = {"a": None, "b": None}

def update_github_file(content, version="a"):
    """Update or create the status file in GitHub repo."""
    if not GITHUB_TOKEN:
        app.logger.error("GITHUB_TOKEN not set")
        return False
    
    file_path = CONTRACTS[version]["status_file"]
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Check if file exists and get its SHA
    get_response = requests.get(api_url, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None
    
    # Prepare payload
    payload = {
        "message": f"Update or create {file_path} from /api/status",
        "content": "",
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha  # Update existing file
    
    # Encode content to base64
    import base64
    payload["content"] = base64.b64encode(json.dumps(content, indent=2).encode()).decode()
    
    # Create or update file
    response = requests.put(api_url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        app.logger.info(f"Successfully updated/created {file_path}: {response.status_code}")
        return True
    else:
        app.logger.error(f"Failed to update/create {file_path}: {response.status_code} - {response.text}")
        return False

def get_contract(version="a"):
    version = version.lower()
    if version not in CONTRACTS:
        return None, "Invalid version (use 'a' or 'b')"
    contract = contracts.get(version)
    if not contract:
        return None, "Contract not initialized"
    return contract, None

@app.route("/api/mint", methods=["POST"])
def mint():
    version = request.args.get("version", "a").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
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
        return jsonify({"error": "Minting failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Mint failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/novena", methods=["POST"])
def start_novena():
    version = request.args.get("version", "a").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
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
        return jsonify({"error": "Novena start failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Novena start failed for stagId {stag_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/checkin", methods=["POST"])
def checkin():
    version = request.args.get("version", "a").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json()
    stag_id = data.get("stagId")
    if not stag_id or not isinstance(stag_id, int):
        return jsonify({"error": "Invalid or missing stagId"}), 400
    try:
        owner = contract.functions.ownerOf(stag_id).call()
        has_novena = contract.functions.hasActiveNovena(stag_id).call()
        if not has_novena:
            return jsonify({"error": f"No active novena for stagId {stag_id}. Start one first."}), 400
        success = True
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
        return jsonify({"error": "Check-in failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"Check-in failed for stagId {stag_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/status", methods=["GET"])
def status():
    version = request.args.get("version", "a").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
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
                    "stake": str(w3.from_wei(stake, "ether"))
                }
                stags.append(stag_data)
            except Exception as e:
                app.logger.error(f"Failed to fetch status for tokenId {token_id}: {e}")
                continue
        sync_success = False
        if stags or not stags:  # Always sync, even if empty, to create file
            sync_success = update_github_file({"stags": stags}, version)
        response = {"stags": stags}
        if not sync_success:
            response["warning"] = "GitHub sync failed - status data not updated in repo"
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Status fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/owner-withdraw", methods=["POST"])
def owner_withdraw():
    version = request.args.get("version", "a").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.withdrawOwnerFunds().build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei"),
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

@app.route("/api/user-withdraw", methods=["POST"])
def user_withdraw():
    version = request.args.get("version", "a").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json()
    user_address = data.get("userAddress")
    if not user_address:
        return jsonify({"error": "Missing userAddress"}), 400
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)  # Simulate user for now
        tx = contract.functions.withdrawPending().build_transaction({
            "from": OWNER_ADDRESS,  # Replace with user_address in production
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            return jsonify({"message": f"Funds withdrawn for {OWNER_ADDRESS}", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "User withdrawal failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        app.logger.error(f"User withdrawal failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "StagQuest Oracle API", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)