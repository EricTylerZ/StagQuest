# test_all.py
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent import StagAgent
from contract import get_nft_status
from config import WALLET_ADDRESS, PRIVATE_KEY, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY

agent = StagAgent()

with open(os.path.join(os.path.dirname(__file__), '..', '..', 'prompts.json')) as f:
    prompts = json.load(f)

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
    print(f"Processing {user_id} for individual {WALLET_ADDRESS}")
    
    day = agent.users[user_id]["day"]
    token_id = agent.users[user_id]["token_id"]
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        msg = prompts[f"Day {day}"][prayer]
        agent.log_message(user_id, day, prayer, msg)
    
    agent.record_response(user_id, day, "Compline", "y")
    
    user = agent.users[user_id]
    if user["day"] != day + 1:
        print(f"Error: {user_id} day should be {day + 1}, got {user['day']}")
        return False
    
    status = get_nft_status(token_id)
    if not status or status["days_completed"] != day or status["successful_days"] != day:
        print(f"Error: NFT status for {token_id} incorrect: {status}")
        return False
    
    print(f"Individual test passed for {user_id}")
    return True

def test_herdmaster():
    print("\n=== Testing Herdmaster with Multiple NFTs ===")
    existing_users = [uid for uid, u in agent.users.items() if u.get("herdmaster") == HERDMASTER_ADDRESS]
    target_num = 3
    if len(existing_users) < target_num:
        for _ in range(target_num - len(existing_users)):
            uid = agent.onboard_user(HERDMASTER_ADDRESS, 3.33, herdmaster_addr=HERDMASTER_ADDRESS, private_key=HERDMASTER_PRIVATE_KEY)
            if uid:
                existing_users.append(uid)
                print(f"Onboarded {uid} under herdmaster {HERDMASTER_ADDRESS}")
    
    if len(existing_users) < target_num:
        print(f"Error: Expected {target_num} users, got {len(existing_users)}")
        return False
    
    for user_id in existing_users[:target_num]:
        day = agent.users[user_id]["day"]
        token_id = agent.users[user_id]["token_id"]
        for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
            msg = prompts[f"Day {day}"][prayer]
            agent.log_message(user_id, day, prayer, msg)
        agent.record_response(user_id, day, "Compline", "y")
        
        user = agent.users[user_id]
        if user["day"] != day + 1:
            print(f"Error: {user_id} day should be {day + 1}, got {user['day']}")
            return False
        
        status = get_nft_status(token_id)
        if not status or status["days_completed"] != day or status["successful_days"] != day:
            print(f"Error: NFT status for {token_id} incorrect: {status}")
            return False
    
    print("Herdmaster test passed")
    return True

def verify_files():
    print("\n=== Verifying Files ===")
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        print(f"Users found: {list(users.keys())}")
    except Exception as e:
        print(f"Error reading users.json: {e}")
        return False
    
    try:
        with open("message_log.json", "r") as f:
            messages = json.load(f)
        print(f"Message entries: {len(messages)}")
    except Exception as e:
        print(f"Error reading message_log.json: {e}")
        return False
    
    return True

def run_all_tests():
    print("Running all tests...")
    individual_passed = test_individual()
    herdmaster_passed = test_herdmaster()
    files_valid = verify_files()
    
    print("\n=== Test Summary ===")
    print(f"Individual Test: {'Passed' if individual_passed else 'Failed'}")
    print(f"Herdmaster Test: {'Passed' if herdmaster_passed else 'Failed'}")
    print(f"File Verification: {'Passed' if files_valid else 'Failed'}")
    
    return individual_passed and herdmaster_passed and files_valid

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("All tests completed successfully!")
    else:
        print("Some tests failed. Check output for details.")