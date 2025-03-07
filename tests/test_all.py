# tests/test_all.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agent import StagAgent
from src.contract import get_nft_status, resolve_day, stake_nft
from src.config import WALLET_ADDRESS, PRIVATE_KEY, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY, OWNER_ADDRESS, OWNER_PRIVATE_KEY

agent = StagAgent()

prompts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts.json')
with open(prompts_file) as f:
    prompts = json.load(f)

def batch_resolve_day(staked_users):
    """Resolve day only for staked NFTs with active novenas."""
    for user_id in staked_users:
        token_id = agent.users[user_id]["token_id"]
        status = get_nft_status(token_id)
        if status and status["has_active_novena"] and agent.users[user_id]["day"] <= 9:
            resolve_day(token_id, True, OWNER_ADDRESS, OWNER_PRIVATE_KEY)
            agent.users[user_id]["day"] += 1
    agent.save_users()

def test_individual():
    print("\n=== Testing Individual NFT Holder ===")
    existing_users = [uid for uid, u in agent.users.items() if u.get("owner") == WALLET_ADDRESS and not u.get("herdmaster")]
    if not existing_users:
        print(f"No existing NFTs for {WALLET_ADDRESS}. Onboarding new user.")
        user_id = agent.onboard_user(WALLET_ADDRESS, 3.33, private_key=PRIVATE_KEY)
        if not user_id:
            print("Individual onboarding failed.")
            return False
        existing_users = [user_id]
    user_id = existing_users[0]
    print(f"Processing {user_id}")
    
    token_id = agent.users[user_id]["token_id"]
    status = get_nft_status(token_id)
    if not status["has_active_novena"] or status["days_completed"] >= 9:
        print(f"{user_id} has no active novena or is complete—re-onboarding.")
        user_id = agent.onboard_user(WALLET_ADDRESS, 3.33, private_key=PRIVATE_KEY)
        if not user_id:
            print("Re-onboarding failed.")
            return False
        token_id = agent.users[user_id]["token_id"]
    
    # Stake the NFT
    stake_tx = stake_nft(token_id, WALLET_ADDRESS, PRIVATE_KEY, total_amount=0.00081, daily_amount=0.00009)
    if not stake_tx:
        print(f"Staking failed for {user_id}")
        return False
    print(f"Staked {user_id} with tx: {stake_tx}")
    
    day = agent.users[user_id]["day"]
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        msg = prompts[f"Day {day}"][prayer]
        agent.log_message(user_id, day, prayer, msg, silent=True)
    
    agent.record_response(user_id, day, "Compline", "y")
    resolve_day(token_id, True, OWNER_ADDRESS, OWNER_PRIVATE_KEY)
    agent.users[user_id]["day"] += 1
    agent.save_users()
    
    user = agent.users[user_id]
    if user["day"] != day + 1:
        print(f"Error: {user_id} day should be {day + 1}, got {user['day']}")
        return False
    
    status = get_nft_status(token_id)
    if not status:
        print(f"Error: Could not fetch NFT status for {token_id}")
        return False
    if status["days_completed"] != day or status["successful_days"] != day:
        print(f"Error: NFT status for {token_id} incorrect: {status}")
        return False
    
    print(f"Individual test passed for {user_id}")
    return True

def test_herdmaster():
    print("\n=== Testing Herdmaster with Multiple NFTs ===")
    existing_users = [uid for uid, u in agent.users.items() if u.get("herdmaster") == HERDMASTER_ADDRESS]
    target_num = 3  # Mint 3 NFTs
    staked_target = 2  # Stake only 2
    if len(existing_users) < target_num:
        for _ in range(target_num - len(existing_users)):
            uid = agent.onboard_user(HERDMASTER_ADDRESS, 3.33, herdmaster_addr=HERDMASTER_ADDRESS, private_key=HERDMASTER_PRIVATE_KEY)
            if uid:
                existing_users.append(uid)
                print(f"Onboarded {uid}")
    
    if len(existing_users) < target_num:
        print(f"Error: Expected {target_num} users, got {len(existing_users)}")
        return False
    
    # Stake only the first 2 NFTs
    staked_users = []
    for user_id in existing_users[:staked_target]:
        print(f"Processing {user_id} for staking")
        token_id = agent.users[user_id]["token_id"]
        status = get_nft_status(token_id)
        if not status["has_active_novena"] or status["days_completed"] >= 9:
            print(f"{user_id} has no active novena or is complete—re-onboarding.")
            user_id = agent.onboard_user(HERDMASTER_ADDRESS, 3.33, herdmaster_addr=HERDMASTER_ADDRESS, private_key=HERDMASTER_PRIVATE_KEY)
            if not user_id:
                print(f"Re-onboarding failed for herdmaster.")
                return False
            token_id = agent.users[user_id]["token_id"]
        
        stake_tx = stake_nft(token_id, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY, total_amount=0.00081, daily_amount=0.00009)
        if not stake_tx:
            print(f"Staking failed for {user_id}")
            return False
        print(f"Staked {user_id} with tx: {stake_tx}")
        staked_users.append(user_id)
    
    # Test messaging and resolve for staked NFTs only
    for user_id in staked_users:
        print(f"Processing {user_id} for messaging")
        day = agent.users[user_id]["day"]
        token_id = agent.users[user_id]["token_id"]
        for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
            msg = prompts[f"Day {day}"][prayer]
            agent.log_message(user_id, day, prayer, msg, silent=True)
        agent.record_response(user_id, day, "Compline", "y")
        
        resolve_day(token_id, True, OWNER_ADDRESS, OWNER_PRIVATE_KEY)
        agent.users[user_id]["day"] += 1
        
        user = agent.users[user_id]
        if user["day"] != day + 1:
            print(f"Error: {user_id} day should be {day + 1}, got {user['day']}")
            return False
        
        status = get_nft_status(token_id)
        if not status:
            print(f"Error: Could not fetch NFT status for {token_id}")
            return False
        if status["days_completed"] != day or status["successful_days"] != day:
            print(f"Error: NFT status for {token_id} incorrect: {status}")
            return False
    
    agent.save_users()
    print("Herdmaster test passed")
    return True

def test_batch_resolve():
    print("\n=== Testing Batch Resolve Day ===")
    staked_users = [uid for uid, u in agent.users.items() if u["day"] <= 9 and get_nft_status(u["token_id"])["stake_remaining"] > 0]
    if not staked_users:
        print("No staked NFTs to process.")
        return False
    
    for user_id in staked_users:
        print(f"Processing {user_id}")
        day = agent.users[user_id]["day"]
        for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
            msg = prompts[f"Day {day}"][prayer]
            agent.log_message(user_id, day, prayer, msg, silent=True)
    
    batch_resolve_day(staked_users)
    
    for user_id in staked_users:
        initial_day = agent.users[user_id]["day"] - 1  # After resolve
        user = agent.users[user_id]
        if user["day"] != initial_day + 1:
            print(f"Error: {user_id} day should be {initial_day + 1}, got {user['day']}")
            return False
        status = get_nft_status(user["token_id"])
        if not status:
            print(f"Error: Could not fetch NFT status for {user['token_id']}")
            return False
        if status["days_completed"] != initial_day or status["successful_days"] != initial_day:
            print(f"Error: NFT status for {user['token_id']} incorrect: {status}")
            return False
    
    print("Batch resolve test passed")
    return True

def verify_files():
    print("\n=== Verifying Files ===")
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json'), "r") as f:
            users = json.load(f)
    except Exception as e:
        print(f"Error reading users.json: {e}")
        return False
    
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'message_log.json'), "r") as f:
            messages = json.load(f)
    except Exception as e:
        print(f"Error reading message_log.json: {e}")
        return False
    
    print(f"Users found: {list(users.keys())}")
    print(f"Message entries: {len(messages)}")
    return True

def run_all_tests():
    print("Running all tests...")
    individual_passed = test_individual()
    herdmaster_passed = test_herdmaster()
    batch_passed = test_batch_resolve()
    files_valid = verify_files()
    
    print("\n=== Test Summary ===")
    print(f"Individual Test: {'Passed' if individual_passed else 'Failed'}")
    print(f"Herdmaster Test: {'Passed' if herdmaster_passed else 'Failed'}")
    print(f"Batch Resolve Test: {'Passed' if batch_passed else 'Failed'}")
    print(f"File Verification: {'Passed' if files_valid else 'Failed'}")
    
    return individual_passed and herdmaster_passed and batch_passed and files_valid

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("All tests completed successfully!")
    else:
        print("Some tests failed. Check output for details.")