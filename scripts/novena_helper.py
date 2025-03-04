# scripts/novena_helper.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, NOVENA_PROCESSOR_ADDRESS, WALLET_ADDRESS, PRIVATE_KEY, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from web3 import Web3

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    novena_abi = json.load(f)

novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=novena_abi)

def get_nft_status(token_id):
    """Fetch NFT status from NovenaProcessor."""
    try:
        days_completed = novena_contract.functions.daysCompleted(token_id).call()
        successful_days = novena_contract.functions.successfulDays(token_id).call()
        has_active = novena_contract.functions.hasActiveNovena(token_id).call()
        stake = novena_contract.functions.stakes(token_id).call()
        daily = novena_contract.functions.dailyStakes(token_id).call()
        return {
            "days_completed": days_completed,
            "successful_days": successful_days,
            "has_active_novena": has_active,
            "stake_remaining": float(w3.from_wei(stake, "ether")),
            "daily_stake": float(w3.from_wei(daily, "ether"))
        }
    except Exception as e:
        print(f"Error getting NFT status: {e}")
        return None

def stake_nft(token_id, address, private_key, total_amount=0.00081, daily_amount=0.00009):
    """Stake an NFT via NovenaProcessor."""
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
            print(f"Staking failed: {tx_hash.hex()}")
            return None
        print(f"Staked with tx: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        print(f"Error staking NFT: {e}")
        return None

def resolve_day(token_id):
    """Resolve a day for an NFT via NovenaProcessor."""
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        tx = novena_contract.functions.resolveDay(token_id, True).build_transaction({
            "from": OWNER_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Resolve day failed: {tx_hash.hex()}")
            return False
        print(f"Resolved day with tx: {tx_hash.hex()}")
        return True
    except Exception as e:
        print(f"Error resolving day: {e}")
        return False

def reset_novena(token_id):
    """Check if novena is complete—no reset action needed with new contract."""
    status = get_nft_status(token_id)
    if status and not status["has_active_novena"] and status["days_completed"] >= 9:
        print(f"Token {token_id} novena complete—no reset needed.")
        return True
    elif status and status["has_active_novena"]:
        print(f"Token {token_id} has active novena—cannot reset.")
        return False
    return False

def process_novena(token_id, address, private_key):
    """Stake and resolve day for an NFT."""
    status = get_nft_status(token_id)
    if status["stake_remaining"] == 0 and not status["has_active_novena"]:
        stake_tx = stake_nft(token_id, address, private_key)
        if not stake_tx:
            print(f"Staking failed for token {token_id}")
            return False
    
    status = get_nft_status(token_id)
    if status["days_completed"] < 9 and status["has_active_novena"]:
        if resolve_day(token_id):
            print(f"Processed novena day for token {token_id}")
            return True
        return False
    print(f"Token {token_id} not eligible for processing")
    return False

if __name__ == "__main__":
    token_id = 1  # Example—adjust as needed
    reset_novena(token_id)
    process_novena(token_id, WALLET_ADDRESS, PRIVATE_KEY)