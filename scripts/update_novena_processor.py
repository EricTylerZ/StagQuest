# scripts/update_novena_processor.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, NOVENA_PROCESSOR_ADDRESS, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from web3 import Web3

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=abi)
NEW_STAG_QUEST = "0xF58C871e0D185C9878E3b96Fb0016665Aa915223"

def update_stag_quest():
    """Update NovenaProcessor to point to the new StagQuest contract."""
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = contract.functions.setStagQuest(NEW_STAG_QUEST).build_transaction({
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
        print(f"Updated NovenaProcessor with tx: {tx_hash.hex()}")
        return True
    except Exception as e:
        print(f"Error updating NovenaProcessor: {e}")
        return False

if __name__ == "__main__":
    print("Updating NovenaProcessor to new StagQuest...")
    update_stag_quest()