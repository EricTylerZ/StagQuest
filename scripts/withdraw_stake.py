# scripts/withdraw_stake.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, WALLET_ADDRESS, PRIVATE_KEY
from web3 import Web3

# Replace with new temporary NovenaProcessor address after deployment
TEMP_NOVENA_PROCESSOR = "0x7659817D69a638111B9fCc141548812597d83F85"

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=TEMP_NOVENA_PROCESSOR, abi=abi)

def withdraw_stake(token_id):
    """Withdraw staked funds from an NFT."""
    try:
        nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
        tx = contract.functions.withdrawStake(token_id).build_transaction({
            "from": WALLET_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Withdraw failed: {tx_hash.hex()}")
            return False
        print(f"Withdrew stake with tx: {tx_hash.hex()}")
        return True
    except Exception as e:
        print(f"Error withdrawing stake: {e}")
        return False

if __name__ == "__main__":
    print("Withdrawing stake for stag-1...")
    withdraw_stake(1)  # stag-1 has 0.00081 ETH staked