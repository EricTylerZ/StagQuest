# tests/test_novena.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, WALLET_ADDRESS, PRIVATE_KEY, NOVENA_PROCESSOR_ADDRESS
from scripts.novena_helper import start_novena
from scripts.resolve_helper import resolve_day
from web3 import Web3

# Load NovenaProcessor ABI
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    novena_abi = json.load(f)

novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=novena_abi)

def test_novena_flow():
    """Test the novena process with NovenaProcessor."""
    token_id = 1  # Replace with a valid token ID
    print(f"\n=== Testing Novena Flow for Token {token_id} ===")
    
    # Start novena
    stake_tx = start_novena(token_id)
    if not stake_tx:
        print("Novena staking failed.")
        return False
    
    # Resolve a day
    resolved = resolve_day(token_id)
    if not resolved:
        print("Day resolution failed.")
        return False
    
    # Verify daysCompleted
    days_completed = novena_contract.functions.daysCompleted(token_id).call()
    print(f"Token {token_id} now has daysCompleted = {days_completed}")
    return True

if __name__ == "__main__":
    test_novena_flow()