# scripts/novena_helper.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, NOVENA_PROCESSOR_ADDRESS, WALLET_ADDRESS, PRIVATE_KEY, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from web3 import Web3

# Load StagQuest ABI (for resolveDay)
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'abi.json'), 'r') as f:
    stag_quest_abi = json.load(f)

# Load NovenaProcessor ABI (for stake and stakes)
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    novena_abi = json.load(f)

stag_quest_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=stag_quest_abi)
novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=novena_abi)

def start_novena(token_id, address=WALLET_ADDRESS, private_key=PRIVATE_KEY, total_amount=0.00081, daily_amount=0.00009):
    """Start a novena by staking an NFT via NovenaProcessor."""
    try:
        current_stake = novena_contract.functions.stakes(token_id).call()
        if current_stake > 0:
            print(f"Token {token_id} already staked with {w3.from_wei(current_stake, 'ether')} ETH. Skipping staking.")
            return None
        nonce = w3.eth.get_transaction_count(address)
        tx = novena_contract.functions.stake(
            token_id,
            w3.to_wei(total_amount, "ether"),
            w3.to_wei(daily_amount, "ether")
        ).build_transaction({
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
            print(f"Failed to start novena for Token {token_id}: {tx_hash.hex()}")
            return None
        print(f"Started novena for Token {token_id} with tx: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        print(f"Error starting novena for Token {token_id}: {e}")
        return None

def advance_novena(token_id, success=True):
    """Advance a novena day for an NFT via StagQuest (onlyOwner)."""
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = stag_quest_contract.functions.resolveDay(token_id, success).build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Failed to advance novena for Token {token_id}: {tx_hash.hex()}")
            return None
        print(f"Advanced novena for Token {token_id} with tx: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        print(f"Error advancing novena for Token {token_id}: {e}")
        return None

if __name__ == "__main__":
    token_id = 1
    start_novena(token_id)  # Check staking status for stag-1
    advance_novena(token_id)  # Advance day for stag-1