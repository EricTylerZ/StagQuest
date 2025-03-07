# scripts/drain_contract.py
import sys
import os
import json  # Added this import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from web3 import Web3

# Load ABI (adjust path if different)
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'abi.json'), 'r') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def withdraw_pending():
    """Withdraw pending funds for the owner."""
    try:
        pending = contract.functions.pendingWithdrawals(OWNER_ADDRESS).call()
        if pending > 0:
            nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
            tx = contract.functions.withdrawPending().build_transaction({
                "from": OWNER_ADDRESS,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": w3.to_wei("2.5", "gwei")
            })
            signed = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Withdrew {pending / 10**18} ETH from pendingWithdrawals: {tx_hash.hex()}")
        else:
            print("No pending withdrawals.")
    except Exception as e:
        print(f"Error withdrawing pending: {e}")

def withdraw_all():
    """Withdraw all contract balance as owner."""
    try:
        balance = w3.eth.get_balance(CONTRACT_ADDRESS)
        if balance > 0:
            nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
            tx = contract.functions.withdraw().build_transaction({
                "from": OWNER_ADDRESS,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": w3.to_wei("2.5", "gwei")
            })
            signed = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Withdrew {balance / 10**18} ETH from contract: {tx_hash.hex()}")
        else:
            print("Contract balance is 0.")
    except Exception as e:
        print(f"Error withdrawing all: {e}")

if __name__ == "__main__":
    print("Draining funds from StagQuest contract...")
    withdraw_pending()
    withdraw_all()
    final_balance = w3.eth.get_balance(CONTRACT_ADDRESS)
    print(f"Final contract balance: {final_balance / 10**18} ETH")