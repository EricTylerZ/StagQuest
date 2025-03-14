import os
import json
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
CORS(app)

# Web3 setup
w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')

# Load ABI from file
with open('data/abi.json', 'r') as abi_file:
    abi = json.load(abi_file)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# GitHub setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "EricTylerZ/StagQuest"
STATUS_FILE = "data/stag_status.json"

def update_github_file(content):
    if not GITHUB_TOKEN:
        return False
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{STATUS_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    get_response = requests.get(api_url, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None
    payload = {"message": f"Update {STATUS_FILE}", "content": "", "branch": "feature/novena-discord"}
    if sha:
        payload["sha"] = sha
    payload["content"] = base64.b64encode(json.dumps(content, indent=2).encode()).decode()
    response = requests.put(api_url, headers=headers, json=payload)
    return response.status_code in [200, 201]

# Mint endpoint
@app.route("/api/mint", methods=["POST"])
def mint():
    try:
        signed_tx = request.json.get("signedTx")
        if not signed_tx:
            return jsonify({"error": "No signed transaction provided"}), 400
        tx_hash = w3.eth.send_raw_transaction(signed_tx)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            token_id = None
            for log in receipt["logs"]:
                if log["topics"][0].hex() == w3.keccak(text="Transfer(address,address,uint256)").hex():
                    token_id = int(log["topics"][3].hex(), 16)
                    break
            if token_id:
                update_github_file(get_status_data())
                return jsonify({"message": "Stag minted", "tokenId": token_id, "txHash": tx_hash.hex()}), 200
            return jsonify({"error": "Mint succeeded but no tokenId found", "txHash": tx_hash.hex()}), 500
        return jsonify({"error": "Minting failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start novena endpoint
@app.route("/api/start-novena", methods=["POST"])
def start_novena():
    try:
        signed_tx = request.json.get("signedTx")
        if not signed_tx:
            return jsonify({"error": "No signed transaction provided"}), 400
        tx_hash = w3.eth.send_raw_transaction(signed_tx)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data())
            return jsonify({"message": "Novena started", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Novena start failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Complete novena endpoint
@app.route("/api/complete-novena", methods=["POST"])
def complete_novena():
    try:
        signed_tx = request.json.get("signedTx")
        if not signed_tx:
            return jsonify({"error": "No signed transaction provided"}), 400
        tx_hash = w3.eth.send_raw_transaction(signed_tx)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data())
            return jsonify({"message": "Novena completed", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Novena completion failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Batch complete novena endpoint
@app.route("/api/batch-complete-novena", methods=["POST"])
def batch_complete_novena():
    try:
        signed_tx = request.json.get("signedTx")
        if not signed_tx:
            return jsonify({"error": "No signed transaction provided"}), 400
        tx_hash = w3.eth.send_raw_transaction(signed_tx)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            update_github_file(get_status_data())
            return jsonify({"message": "Batch novena completion successful", "txHash": tx_hash.hex()}), 200
        return jsonify({"error": "Batch completion failed", "txHash": tx_hash.hex()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Status endpoint
def get_status_data():
    try:
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
                    "familySize": int(family_size),
                    "hasActiveNovena": has_novena,
                    "successfulDays": int(successful_days)
                })
            except Exception:
                continue
        return {"stags": stags}
    except Exception:
        return {"stags": []}

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(get_status_data()), 200

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)