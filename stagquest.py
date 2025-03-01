from web3 import Web3
from dotenv import load_dotenv
import os
import json

load_dotenv()

w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
contract_addr = "0xfE745e106CF1C837b3A0e39f0528B2e67be8f9c4"
with open("abi.json") as f:
    abi = json.load(f)
contract = w3.eth.contract(address=contract_addr, abi=abi)

user_addr = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")
w3.eth.default_account = user_addr

nonce = w3.eth.get_transaction_count(user_addr)

# Mint
tx = contract.functions.mint().build_transaction({
    "from": user_addr,
    "value": w3.to_wei(0.001, "ether"),
    "nonce": nonce,
    "gas": 200000,
    "gasPrice": w3.to_wei("0.5", "gwei")
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Minted: {tx_hash.hex()}")

# Stake
nonce += 1
tx = contract.functions.stake().build_transaction({
    "from": user_addr,
    "value": w3.to_wei(0.009, "ether"),
    "nonce": nonce,
    "gas": 200000,
    "gasPrice": w3.to_wei("0.5", "gwei")
})
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Staked: {tx_hash.hex()}")

# Load prompts
with open("prompts.json") as f:
    prompts = json.load(f)

# Novena (3 days)
regen_addr = w3.to_checksum_address("0x1234567890abcdef1234567890abcdef12345678")
for day in range(1, 4):
    day_key = f"Day {day}"
    print(f"\n{day_key}:")
    for prayer, msg in prompts[day_key].items():
        print(f"{prayer}: {msg}")
    response = input("Success? (y/n): ")
    success = response.lower() == "y"
    nonce += 1
    tx = contract.functions.resolveDay(success, regen_addr).build_transaction({
        "from": user_addr,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("0.5", "gwei")
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"{day_key} Tx: {tx_hash.hex()}")