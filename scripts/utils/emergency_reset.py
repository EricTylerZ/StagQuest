# emergency_reset.py
from web3 import Web3
from dotenv import load_dotenv
from pathlib import Path 
import os
import json
import time

# Get script directory
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent.parent  # Goes up utils → scripts → project root

# Load files from project root
load_dotenv(dotenv_path=project_root/'.env')

with open(project_root/'abi.json') as f:  # Correct path
    abi = json.load(f)

load_dotenv(dotenv_path=Path('..')/'.env')  # Windows path fix
w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
contract_addr = "0xfE745e106CF1C837b3A0e39f0528B2e67be8f9c4"

contract = w3.eth.contract(address=contract_addr, abi=abi)
user_addr = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")

current_stake = contract.functions.stakes(user_addr).call()
print(f"Current stake: {w3.from_wei(current_stake, 'ether')} ETH")

days_stuck = current_stake // w3.to_wei(0.001, "ether")
print(f"Need to resolve {days_stuck} days")

# Get initial nonce and track manually
nonce = w3.eth.get_transaction_count(user_addr)

for day in range(1, days_stuck + 1):
    print(f"\nResolving fake day {day}")
    
    try:
        tx = contract.functions.resolveDay(True, user_addr).build_transaction({
            "from": user_addr,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("1.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        print(f"Reset tx {day}: {tx_hash.hex()}")
        
        # Wait for transaction to be mined
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status == 1:
            print(f"Confirmed in block {receipt.blockNumber}")
            nonce += 1  # Only increment after successful confirmation
        else:
            print("Transaction failed!")
            break
            
    except Exception as e:
        print(f"Error on day {day}: {str(e)}")
        print("Retrying with new nonce...")
        nonce = w3.eth.get_transaction_count(user_addr)  # Refresh nonce
        time.sleep(5)