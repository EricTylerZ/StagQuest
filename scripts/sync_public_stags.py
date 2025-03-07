# scripts/sync_public_stags.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.sync_stags import sync_stags

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
USERS_FILE = os.path.join(data_dir, "users.json")
PUBLIC_USERS_FILE = os.path.join(data_dir, "public_users.json")

def sync_public_stags():
    sync_stags()
    
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    
    public_users = {}
    for user_id, data in users.items():
        public_users[user_id] = {
            "user_id": user_id,
            "token_id": data["token_id"],
            "day": data["day"],
            "days_completed": data["days_completed"],
            "total_staked": data["total_staked"],
            "stake_remaining": data["stake_remaining"],
            "stake_tx": data["stake_tx"]
        }
    
    with open(PUBLIC_USERS_FILE, "w") as f:
        json.dump(public_users, f, indent=4)
    print(f"Generated public_users.json with {len(public_users)} stags: {list(public_users.keys())}")

if __name__ == "__main__":
    sync_public_stags()