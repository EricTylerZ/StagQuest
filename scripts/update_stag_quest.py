# scripts/update_stag_quest.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from web3 import Web3

NEW_NOVENA_PROCESSOR = "0x33ce117015a834D2631d72f4Fe13C26366E5F5BA"

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'abi.json'), 'r') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def update_novena_processor():
    """Update StagQuest to point to the new NovenaProcessor."""
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.setNovenaProcessor(NEW_NOVENA_PROCESSOR).build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Update failed: {tx_hash.hex()}")
            return False
        print(f"Updated StagQuest with tx: {tx_hash.hex()}")
        return True
    except Exception as e:
        print(f"Error updating StagQuest: {e}")
        return False

if __name__ == "__main__":
    print("Updating StagQuest to new NovenaProcessor...")
    update_novena_processor()