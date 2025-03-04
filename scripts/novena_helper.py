# scripts/novena_helper.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, WALLET_ADDRESS, PRIVATE_KEY, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from src.contract import get_nft_status, stake_nft, resolve_day

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'abi.json'), 'r') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def reset_novena(token_id):
    """Check and reset novena if complete."""
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
    if status["stake_remaining"] == 0:
        stake_tx = stake_nft(token_id, address, private_key, total_amount=0.00081, daily_amount=0.00009)
        if not stake_tx:
            print(f"Staking failed for token {token_id}")
            return False
        print(f"Staked token {token_id} with tx: {stake_tx}")
    
    if status["days_completed"] < 9 and status["has_active_novena"]:
        resolve_day(token_id, True, OWNER_ADDRESS, OWNER_PRIVATE_KEY)
        print(f"Resolved day for token {token_id}")
        return True
    return False

if __name__ == "__main__":
    token_id = 1  # Example—adjust as needed
    reset_novena(token_id)
    process_novena(token_id, WALLET_ADDRESS, PRIVATE_KEY)