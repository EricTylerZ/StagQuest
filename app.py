# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
from src.config import w3, CONTRACT_ADDRESS_C, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from time import time
import requests
import json
import base64

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})  # Allow localhost for dev

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "EricTylerZ/StagQuest"
ABI_URL = f"https://raw.githubusercontent.com/EricTylerZ/StagQuest/version-b/data/abi.json?t={int(time())}"
CONTRACTS = {"b": {"address": CONTRACT_ADDRESS_C, "status_file": "data/stag_status_b.json"}}

try:
    abi = requests.get(ABI_URL).json()
    contracts = {"b": w3.eth.contract(address=CONTRACT_ADDRESS_C, abi=abi)}
except Exception as e:
    app.logger.error(f"Failed to load ABI: {e}")
    contracts = {"b": None}

def update_github_file(content, version="b"):
    if not GITHUB_TOKEN:
        return False
    file_path = CONTRACTS[version]["status_file"]
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    get_response = requests.get(api_url, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None
    payload = {"message": f"Update {file_path}", "content": base64.b64encode(json.dumps(content, indent=2).encode()).decode(), "branch": "version-b"}
    if sha:
        payload["sha"] = sha
    response = requests.put(api_url, headers=headers, json=payload)
    return response.status_code in [200, 201]

def get_contract(version="b"):
    contract = contracts.get(version.lower())
    return contract, None if contract else "Contract not initialized"

@app.route("/api/mint", methods=["POST"])
def mint():
    contract, error = get_contract()
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json() or {}
    amount = data.get("amount", "0.0001")
    user_address = data.get("address")
    if not w3.is_address(user_address):
        return jsonify({"error": "Invalid address"}), 400
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.mintStag().build_transaction({
            "from": OWNER_ADDRESS,
            "value": w3.to_wei(amount, "ether"),
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            token_id = int([log["topics"][3].hex() for log in receipt["logs"] if log["topics"][0].hex() == w3.keccak(text="Transfer(address,address,uint256)").hex()][0], 16)
            update_github_file(get_status_data(contract))
            return jsonify({"message": "Stag minted", "tokenId": token_id, "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Minting failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/novena", methods=["POST"])
def start_novena():
    contract, error = get_contract()
    if error:
        return jsonify({"error": error}), 500
    data = request.get_json() or {}
    stag_id = data.get("stagId")
    amount = data.get("amount", "0")
    user_address = data.get("address")
    if not stag_id or not isinstance(stag_id, int) or not w3.is_address(user_address):
        return jsonify({"error": "Invalid stagId or address"}), 400
    try:
        owner = contract.functions.ownerOf(stag_id).call()
        if owner.lower() != user_address.lower():
            return jsonify({"error": "You don’t own this Stag Artistic"}), 403
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.startNovena(stag_id).build_transaction({
            "from": OWNER_ADDRESS,
            "value": w3.to_wei(amount, "ether"),
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.to_wei("5", "gwei"),
            "chainId": 84532
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data(contract))
            return jsonify({"message": f"Novena started for stagId {stag_id}", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Novena start failed"}), 500
    except Exception as e:
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
                stags.append({
                    "tokenId": token_id,
                    "owner": owner,
                    "familySize": family_size,
                    "hasActiveNovena": has_novena,
                    "successfulDays": successful_days
                })
            except Exception:
                continue
        return {"stags": stags}
    except Exception as e:
        return {"stags": [], "error": str(e)}

@app.route("/api/status", methods=["GET"])
def status():
    contract, error = get_contract()
    if error:
        return jsonify({"error": error}), 500
    return jsonify(get_status_data(contract)), 200

@app.route("/", methods=["GET"])
def home():
    return "StagQuest API", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)