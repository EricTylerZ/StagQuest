# scripts/sync_stags.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, WALLET_ADDRESS, HERDMASTER_ADDRESS
from src.contract import get_tokens_by_owner, get_nft_status

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def get_mint_tx(token_id):
    """Fetch mint transaction hash for a token_id via Transfer event."""
    try:
        # Use the contract instance from get_nft_status
        status = get_nft_status(token_id)  # Ensure contract is initialized
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=get_nft_status.__globals__['_get_contract']().abi)
        
        zero_address = "0x0000000000000000000000000000000000000000"
        events = contract.events.Transfer.get_logs(
            fromBlock=0,
            toBlock='latest',
            argument_filters={"from": zero_address, "tokenId": token_id}
        )
        if events:
            return events[0].transactionHash.hex()
        return "unknown"
    except Exception as e:
        print(f"Error fetching mint tx for token {token_id}: {e}")
        return "unknown"

def sync_stags():
    users = {}
    addresses = [WALLET_ADDRESS, HERDMASTER_ADDRESS]
    for addr in addresses:
        token_ids = get_tokens_by_owner(addr)
        for token_id in token_ids:
            status = get_nft_status(token_id)
            if status:
                user_id = f"stag-{token_id}"
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
                    "mint_tx": mint_tx
                }
                if addr == HERDMASTER_ADDRESS:
                    user_data["herdmaster"] = HERDMASTER_ADDRESS
                users[user_id] = user_data
    
    users_file = os.path.join(data_dir, 'users.json')
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)
    print(f"Synced {len(users)} stags to users.json: {list(users.keys())}")

if __name__ == "__main__":
    sync_stags()