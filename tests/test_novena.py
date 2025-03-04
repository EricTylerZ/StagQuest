# tests/test_novena.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agent import StagAgent
from src.contract import get_nft_status
from src.config import WALLET_ADDRESS, PRIVATE_KEY, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY
from scripts.mint_helper import mint_nft
from scripts.novena_helper import process_novena, reset_novena
from scripts.sync_stags import sync_stags

agent = StagAgent()

prompts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts.json')
with open(prompts_file) as f:
    prompts = json.load(f)

def test_individual_novena():
    print("\n=== Testing Individual Novena ===")
    existing_users = [uid for uid, u in agent.users.items() if u.get("owner") == WALLET_ADDRESS and not u.get("herdmaster")]
    
    if not existing_users:
        print(f"No NFTs for {WALLET_ADDRESS}—minting new one.")
        tx_hash, token_id = mint_nft(WALLET_ADDRESS, PRIVATE_KEY)
        if not tx_hash:
            print("Minting failed for individual—expected if prior NFT exists.")
            return False
        user_id = f"stag-{token_id}"
        agent.users[user_id] = {
            "contract_address": "0xF58C871e0D185C9878E3b96Fb0016665Aa915223",
            "owner": WALLET_ADDRESS,
            "token_id": token_id,
            "day": 1,
            "days_completed": 0,
            "responses": {},
            "fiat_paid": 3.33,
            "timezone_offset": -7,
            "mint_tx": tx_hash,
            "stake_tx": "unknown",
            "total_staked": 0.0,
            "stake_remaining": 0.0,
            "daily_stake": 0.0
        }
        agent.save_users()
        sync_stags()  # Resync after minting
    else:
        user_id = existing_users[0]
        token_id = agent.users[user_id]["token_id"]
        status = get_nft_status(token_id)
        if status["has_active_novena"]:
            print(f"{user_id} has active novena—cannot mint new NFT, processing existing.")
        else:
            print(f"{user_id} has no active novena—should allow minting, but using existing for test.")
    
    # Process existing or new NFT
    if not process_novena(token_id, WALLET_ADDRESS, PRIVATE_KEY):
        print(f"Failed to process novena for {user_id}")
        return False
    
    day = agent.users[user_id]["day"]
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        msg = prompts[f"Day {day}"][prayer]
        agent.log_message(user_id, day, prayer, msg, silent=True)
    agent.record_response(user_id, day, "Compline", "y")
    agent.users[user_id]["day"] += 1
    agent.save_users()
    sync_stags()  # Resync after processing
    
    status = get_nft_status(token_id)
    if status["days_completed"] != day or status["successful_days"] != day:
        print(f"Error: NFT status for {token_id} incorrect: {status}")
        return False
    
    print(f"Individual novena test passed for {user_id}")
    return True

def test_herdmaster_novena():
    print("\n=== Testing Herdmaster Novena ===")
    target_num = 3
    staked_target = 1
    existing_users = [uid for uid, u in agent.users.items() if u.get("herdmaster") == HERDMASTER_ADDRESS]
    
    # Mint up to 3 NFTs
    while len(existing_users) < target_num:
        tx_hash, token_id = mint_nft(HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY)
        if not tx_hash:
            print("Minting failed for herdmaster—unexpected for herdmaster.")
            return False
        user_id = f"stag-{token_id}"
        agent.users[user_id] = {
            "contract_address": "0xF58C871e0D185C9878E3b96Fb0016665Aa915223",
            "owner": HERDMASTER_ADDRESS,
            "token_id": token_id,
            "day": 1,
            "days_completed": 0,
            "responses": {},
            "fiat_paid": 3.33,
            "timezone_offset": -7,
            "mint_tx": tx_hash,
            "stake_tx": "unknown",
            "total_staked": 0.0,
            "stake_remaining": 0.0,
            "daily_stake": 0.0,
            "herdmaster": HERDMASTER_ADDRESS
        }
        existing_users.append(user_id)
        agent.save_users()
        sync_stags()  # Resync after each mint
    
    # Stake only 1 NFT
    staked_users = []
    user_id = existing_users[0]
    token_id = agent.users[user_id]["token_id"]
    if not process_novena(token_id, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY):
        print(f"Failed to process novena for {user_id}")
        return False
    staked_users.append(user_id)
    
    # Process messaging for staked NFT
    for user_id in staked_users:
        day = agent.users[user_id]["day"]
        token_id = agent.users[user_id]["token_id"]
        for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
            msg = prompts[f"Day {day}"][prayer]
            agent.log_message(user_id, day, prayer, msg, silent=True)
        agent.record_response(user_id, day, "Compline", "y")
        agent.users[user_id]["day"] += 1
    
    agent.save_users()
    sync_stags()  # Resync after processing
    
    for user_id in staked_users:
        token_id = agent.users[user_id]["token_id"]
        status = get_nft_status(token_id)
        if status["days_completed"] != day or status["successful_days"] != day:
            print(f"Error: NFT status for {token_id} incorrect: {status}")
            return False
    
    print("Herdmaster novena test passed")
    return True

def run_all_tests():
    print("Running all novena tests...")
    sync_stags()  # Single sync for all tests
    individual_passed = test_individual_novena()
    herdmaster_passed = test_herdmaster_novena()
    
    print("\n=== Test Summary ===")
    print(f"Individual Novena Test: {'Passed' if individual_passed else 'Failed'}")
    print(f"Herdmaster Novena Test: {'Passed' if herdmaster_passed else 'Failed'}")
    
    return individual_passed and herdmaster_passed

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("All novena tests completed successfully!")
    else:
        print("Some tests failed. Check output for details.")