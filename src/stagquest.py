from web3 import Web3
from dotenv import load_dotenv
import os
import json
import time

# Initialize
load_dotenv()
w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
contract_addr = "0xfE745e106CF1C837b3A0e39f0528B2e67be8f9c4"

with open("abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_addr, abi=abi)
user_addr = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
w3.eth.default_account = user_addr

# 1. Mint NFT if needed
if contract.functions.balanceOf(user_addr).call() == 0:
    mint_nonce = w3.eth.get_transaction_count(user_addr)
    tx = contract.functions.mint().build_transaction({
        "from": user_addr,
        "value": w3.to_wei(0.001, "ether"),
        "nonce": mint_nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Minted: {tx_hash.hex()}")

# 2. Stake Management
required_stake = w3.to_wei(0.009, "ether")
current_stake = contract.functions.stakes(user_addr).call()

# Initialize master nonce
nonce = w3.eth.get_transaction_count(user_addr)

if current_stake < required_stake:
    additional_needed = required_stake - current_stake
    print(f"Staking additional {w3.from_wei(additional_needed, 'ether')} ETH")
    
    tx = contract.functions.stake().build_transaction({
        "from": user_addr,
        "value": additional_needed,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Staked: {tx_hash.hex()}")
    nonce += 1  # Increment after confirmation

# 3. Load Prompts
try:
    with open("prompts.json") as f:
        prompts = json.load(f)
except FileNotFoundError:
    print("Missing prompts.json!")
    exit(1)

# 4. Novena Execution
regen_addr = w3.to_checksum_address("0x2e0AA552E490Db6219C304a6b280e3DeA6962813")

for day in range(1, 10):
    print(f"\nDAY {day} COMBAT:")
    for prayer, msg in prompts[f"Day {day}"].items():
        print(f"{prayer}: {msg}")
    
    # Input validation
    while True:
        victory = input("\nDid you defeat pornography today? (y/n): ").lower()
        if victory in ['y', 'n']: break
        print("Invalid input! Only 'y'/'n' accepted")
    
    # Send resolution
    tx = contract.functions.resolveDay(victory == 'y', regen_addr).build_transaction({
        "from": user_addr,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    
    # Wait and increment
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        print(f"Day {day} failed! Check tx {tx_hash.hex()}")
        exit()
    nonce += 1
    print(f"Day {day} confirmed in block {receipt.blockNumber}")

print("\nStagQuest Novena COMPLETE! 0.001 ETH/day was returned to you each day you were successful, or sent to an anti-human trafficking project if you fell and needed to stand back up. You're welcome to get back in the fight for a new Novena to end human sex trafficking, the world needs warriors.")