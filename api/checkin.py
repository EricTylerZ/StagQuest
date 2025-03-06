# api/checkin.py
from flask import Flask, request, jsonify
import requests
from web3 import Web3
from src.config import RPC_URL, CONTRACT_ADDRESS, ORACLE_ADDRESS, ORACLE_PRIVATE_KEY, w3

app = Flask(__name__)

# Load ABI from GitHub
ABI_URL = "https://raw.githubusercontent.com/EricTylerZ/StagQuest/main/data/abi.json"

def load_json_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to load {url}: Status {response.status_code}")

abi = load_json_from_url(ABI_URL)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

@app.route("/api/checkin", methods=["POST"])
def checkin():
    data = request.get_json()
    stag_id = data.get("stagId")
    if not stag_id or not isinstance(stag_id, int):
        return jsonify({"error": "Invalid or missing stagId"}), 400

    # Simulate success for now (replace with real logic later)
    success = True  # Will be updated based on your needs (e.g., Twilio response)

    # Build and send transaction using oracle credentials
    nonce = w3.eth.get_transaction_count(ORACLE_ADDRESS)
    txn = contract.functions.checkIn(stag_id, success).build_transaction({
        "from": ORACLE_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "chainId": 84532  # Base Sepolia
    })
    signed_txn = w3.eth.account.sign_transaction(txn, ORACLE_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return jsonify({"stagId": stag_id, "success": success, "txHash": tx_hash.hex()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))