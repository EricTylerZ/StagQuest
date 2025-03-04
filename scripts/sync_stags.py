# scripts/sync_stags.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CONTRACT_ADDRESS, WALLET_ADDRESS, HERDMASTER_ADDRESS
from src.contract import get_tokens_by_owner, get_nft_status
from src.utils import get_stake_tx, get_mint_tx

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def sync_stags():
    users = {}
    addresses = [WALLET_ADDRESS, HERDMASTER_ADDRESS]
    for addr in addresses:
        token_ids = get_tokens_by_owner(addr)
        for token_id in token_ids:
            status = get_nft_status(token_id)
            if status:
                user_id = f"stag-{token_id}"
                stake_tx, total_staked = get_stake_tx(token_id)
                mint_tx = get_mint_tx(token_id)
                user_data = {
                    "contract_address": CONTRACT_ADDRESS,
                    "owner": status["owner"],
                    "token_id": token_id,
                    "day": status["days_completed"] + 1 if status["has_active_novena"] else 10,
                    "days_completed": status["days_completed"],
                    "responses": {},
                    "fiat_paid": 3.33,
                    "timezone_offset": -7,
                    "mint_tx": mint_tx,
                    "stake_tx": stake_tx,
                    "total_staked": total_staked,
                    "stake_remaining": float(status["stake_remaining"]),
                    "daily_stake": float(status["daily_stake"])
                }
                if addr == HERDMASTER_ADDRESS:
                    user_data["herdmaster"] = HERDMASTER_ADDRESS
                users[user_id] = user_data
    
    users_file = os.path.join(data_dir, "users.json")
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)
    print(f"Synced {len(users)} stags to users.json: {list(users.keys())}")

if __name__ == "__main__":
    sync_stags()