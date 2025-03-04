# scripts/sync_public_stags.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3
from scripts.sync_stags import sync_stags  # Import original sync function

# Absolute path to data directory
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
USERS_FILE = os.path.join(data_dir, 'users.json')
PUBLIC_USERS_FILE = os.path.join(data_dir, 'public_users.json')

def get_mint_eth(mint_tx):
    """Fetch ETH value from a mint transaction hash."""
    try:
        if mint_tx == "unknown":
            return 0.0  # Default if no tx hash
        tx = w3.eth.get_transaction(mint_tx)
        eth_value = w3.from_wei(tx['value'], 'ether')  # Convert wei to ETH
        return float(eth_value)
    except Exception as e:
        print(f"Error fetching tx {mint_tx}: {e}")
        return 0.0

def sync_public_stags():
    """Generate public_users.json with staking data from users.json."""
    # Run original sync to ensure users.json is fresh
    sync_stags()
    
    # Read private users.json
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    public_users = {}
    for user_id, data in users.items():
        eth_staked = get_mint_eth(data.get('mint_tx', 'unknown'))
        public_users[user_id] = {
            "user_id": user_id,
            "token_id": data["token_id"],
            "day": data["day"],
            "days_completed": data["days_completed"],
            "eth_staked": eth_staked
        }
    
    # Write public_users.json
    with open(PUBLIC_USERS_FILE, 'w') as f:
        json.dump(public_users, f, indent=4)
    
    print(f"Generated public_users.json with {len(public_users)} stags: {list(public_users.keys())}")

if __name__ == "__main__":
    sync_public_stags()