# scripts/resolve_helper.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, NOVENA_PROCESSOR_ADDRESS, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from web3 import Web3

# Load NovenaProcessor ABI
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    novena_abi = json.load(f)

novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=novena_abi)

def resolve_day(token_id):
    """Resolve a day for an NFT via NovenaProcessor."""
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = novena_contract.functions.resolveDay(token_id, True).build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Failed to resolve day for Token {token_id}: {tx_hash.hex()}")
            return False
        print(f"Resolved day for Token {token_id} with tx: {tx_hash.hex()}")
        return True
    except Exception as e:
        print(f"Error resolving day for Token {token_id}: {e}")
        return False