# test_all.py
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent import StagAgent
from contract import get_nft_status
from config import WALLET_ADDRESS, PRIVATE_KEY, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY

# Initialize agent
agent = StagAgent()

# Load prompts
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'prompts.json')) as f:
    prompts = json.load(f)

def test_individual():
    print("\n=== Testing Individual NFT Holder ===")
    # Onboard one user
    user_id = agent.onboard_user(WALLET_ADDRESS, 3.33, timezone_offset=-7, private_key=PRIVATE_KEY)
    if not user_id:
        print("Individual onboarding failed.")
        return False
    
    print(f"Onboarded {user_id} as individual with address {WALLET_ADDRESS}")
    
    # Log messages for Day 1
    user = agent.users[user_id]
    day = user["day"]
    token_id = user["token_id"]
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        msg = prompts[f"Day {day}"][prayer]
        agent.log_message(user_id, day, prayer, msg)
    
    # Simulate responses
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        agent.record_response(user_id, day, prayer, "y")
    
    # Verify results
    user = agent.users[user_id]
    if user["day"] != 2:
        print(f"Error: {user_id} day should be 2, got {user['day']}")
        return False
    
    status = get_nft_status(token_id)
    if not status or status["days_completed"] != 1 or status["successful_days"] != 1:
        print(f"Error: NFT status for {token_id} incorrect: {status}")
        return False
    
    print(f"Individual test passed for {user_id}")
    return True

def test_herdmaster():
    print("\n=== Testing Herdmaster with Multiple NFTs ===")
    # Onboard three users
    user_ids = []
    for _ in range(3):
        uid = agent.onboard_user(HERDMASTER_ADDRESS, 3.33, timezone_offset=-7, 
                               herdmaster_addr=HERDMASTER_ADDRESS, private_key=HERDMASTER_PRIVATE_KEY)
        if uid:
            user_ids.append(uid)
            print(f"Onboarded {uid} under herdmaster {HERDMASTER_ADDRESS}")
    
    if len(user_ids) != 3:
        print(f"Error: Expected 3 users, got {len(user_ids)}")
        return False
    
    # Process one user’s Day 1
    user_id = user_ids[0]
    user = agent.users[user_id]
    day = user["day"]
    token_id = user["token_id"]
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        msg = prompts[f"Day {day}"][prayer]
        agent.log_message(user_id, day, prayer, msg)
    
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        agent.record_response(user_id, day, prayer, "y")
    
    # Verify results
    user = agent.users[user_id]
    if user["day"] != 2:
        print(f"Error: {user_id} day should be 2, got {user['day']}")
        return False
    
    status = get_nft_status(token_id)
    if not status or status["days_completed"] != 1 or status["successful_days"] != 1:
        print(f"Error: NFT status for {token_id} incorrect: {status}")
        return False
    
    # Check other users remain at Day 1
    for uid in user_ids[1:]:
        if agent.users[uid]["day"] != 1:
            print(f"Error: {uid} day should be 1, got {agent.users[uid]['day']}")
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