# scripts/novena_helper.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, NOVENA_PROCESSOR_ADDRESS, WALLET_ADDRESS, PRIVATE_KEY, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY
from web3 import Web3

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    novena_abi = json.load(f)

novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=novena_abi)

def start_novena(token_id, address, private_key, total_amount=0.00081, daily_amount=0.00009):
    """Start a novena by staking an NFT via NovenaProcessor."""
    try:
        nonce = w3.eth.get_transaction_count(address)
        tx = novena_contract.functions.stake(token_id, w3.to_wei(total_amount, "ether"), w3.to_wei(daily_amount, "ether")).build_transaction({
            "from": address,
            "value": w3.to_wei(total_amount, "ether"),
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Starting novena failed: {tx_hash.hex()}")
            return None
        print(f"Started novena with tx: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        print(f"Error starting novena: {e}")
        return None

if __name__ == "__main__":
    token_id = 1  # Example—adjust as needed
    start_novena(token_id, WALLET_ADDRESS, PRIVATE_KEY)