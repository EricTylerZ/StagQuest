# scripts/sync_users_json.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, NOVENA_PROCESSOR_ADDRESS, WALLET_ADDRESS, HERDMASTER_ADDRESS
from web3 import Web3

# Load NovenaProcessor ABI (ensure this is for NovenaProcessor.sol)
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'novena_abi.json'), 'r') as f:
    abi = json.load(f)

# Initialize the NovenaProcessor contract
novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=abi)

def get_stag_status(token_id):
    """Fetch the current blockchain status for a given NFT token ID from NovenaProcessor."""
    try:
        stakes = novena_contract.functions.stakes(token_id).call()
        daily_stakes = novena_contract.functions.dailyStakes(token_id).call()
        days_completed = novena_contract.functions.daysCompleted(token_id).call()
        has_active_novena = novena_contract.functions.hasActiveNovena(token_id).call()
        return {
            "total_staked": float(w3.from_wei(stakes, "ether")),
            "daily_stake": float(w3.from_wei(daily_stakes, "ether")),
            "days_completed": days_completed,
            "has_active_novena": has_active_novena
        }
    except Exception as e:
        print(f"Error fetching status for Token {token_id}: {e}")
        return None

def sync_users_json():
    """Update users.json to match the NovenaProcessor blockchain state."""
    users_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
    
    # Load existing users.json
    try:
        with open(users_file, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"{users_file} not found. Starting with empty users dict.")
        users = {}
    
    # Update each user's data
    for user_id, user_data in users.items():
        token_id = user_data["token_id"]
        status = get_stag_status(token_id)
        if status:
            # Update fields with blockchain values
            user_data["total_staked"] = status["total_staked"]
            user_data["daily_stake"] = status["daily_stake"]
            user_data["days_completed"] = status["days_completed"]
            
            # Set "day" based on novena status
            if status["has_active_novena"]:
                user_data["day"] = status["days_completed"] + 1  # Current day in progress
            elif status["days_completed"] == 9:
                user_data["day"] = 10  # Novena completed
            else:
                user_data["day"] = 0  # No active novena
        else:
            print(f"Skipping Token {token_id}: Could not fetch status")
    
    # Save updated users.json
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)
    print("Successfully synced users.json with NovenaProcessor state.")

if __name__ == "__main__":
    print(f"Using NovenaProcessor at: {NOVENA_PROCESSOR_ADDRESS}")
    sync_users_json()