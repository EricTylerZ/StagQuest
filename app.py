# app.py
import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
from src.config import w3, CONTRACT_ADDRESS_C

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://stag-quest.vercel.app"]}})

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "EricTylerZ/StagQuest"

CONTRACTS = {
    "b": {"address": CONTRACT_ADDRESS_C, "status_file": "data/stag_status_b.json"}
}

ABI_URL = f"https://raw.githubusercontent.com/EricTylerZ/StagQuest/version-b/data/abi.json?t={int(time())}"

def load_json_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to load {url}: Status {response.status_code}")

try:
    abi = load_json_from_url(ABI_URL)
    contracts = {"b": w3.eth.contract(address=CONTRACT_ADDRESS_C, abi=abi)}
except Exception as e:
    contracts = {"b": None}

def get_contract(version="b"):
    version = version.lower()
    if version not in CONTRACTS:
        return None, "Invalid version (use 'b')"
    contract = contracts.get(version)
    if not contract:
        return None, "Contract not initialized"
    return contract, None

def get_status_data(contract):
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
                    "familySize": int(family_size),  # Convert uint8 to int
                    "hasActiveNovena": has_novena,
                    "successfulDays": int(successful_days)  # Convert uint8 to int
                })
            except:
                continue
        return {"stags": stags}
    except Exception as e:
        return {"stags": [], "error": str(e)}

@app.route("/api/status", methods=["GET"])
def status():
    version = request.args.get("version", "b").lower()
    contract, error = get_contract(version)
    if error:
        return jsonify({"error": error}), 500
    status_data = get_status_data(contract)
    if "error" in status_data:
        return jsonify(status_data), 500
    return jsonify(status_data), 200

@app.route("/", methods=["GET"])
def home():
    return "StagQuest API", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)