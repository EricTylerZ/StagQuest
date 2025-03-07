# scripts/check_days_completed.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, NOVENA_PROCESSOR_ADDRESS
from web3 import Web3

# Load NovenaProcessor ABI
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    novena_abi = json.load(f)

# Initialize contract
novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=novena_abi)

def check_days_completed(token_id):
    """Check daysCompleted for a given token ID and flag if >= 9."""
    try:
        days_completed = novena_contract.functions.daysCompleted(token_id).call()
        print(f"Token {token_id}: daysCompleted = {days_completed}")
        if days_completed >= 9:
            print(f"WARNING: Token {token_id} is potentially stuck with daysCompleted = {days_completed}")
        return days_completed
    except Exception as e:
        print(f"Error checking Token {token_id}: {e}")
        return None

if __name__ == "__main__":
    # List of token IDs to check (replace with your actual token IDs)
    token_ids = [1, 2, 3, 4]  # Example IDs—update as needed
    print("Checking daysCompleted for stags...")
    for token_id in token_ids:
        check_days_completed(token_id)