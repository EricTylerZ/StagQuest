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

agent = StagAgent()

prompts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts.json')
with open(prompts_file) as f:
    prompts = json.load(f)

def test_individual_novena():
    print("\n=== Testing Individual Novena ===")
    user_id = agent.onboard_user(WALLET_ADDRESS, 3.33, private_key=PRIVATE_KEY)
    if not user_id:
        print("Onboarding failed.")
        return False
    
    token_id = agent.users[user_id]["token_id"]
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
    
    status = get_nft_status(token_id)
    if status["days_completed"] != day or status["successful_days"] != day:
        print(f"Error: NFT status for {token_id} incorrect: {status}")
        return False
    
    print(f"Individual novena test passed for {user_id}")
    return True

def test_herdmaster_novena():
    print("\n=== Testing Herdmaster Novena ===")
    target_num = 3
    staked_target = 2
    existing_users = [uid for uid, u in agent.users.items() if u.get("herdmaster") == HERDMASTER_ADDRESS]
    
    if len(existing_users) < target_num:
        for _ in range(target_num - len(existing_users)):
            uid = agent.onboard_user(HERDMASTER_ADDRESS, 3.33, herdmaster_addr=HERDMASTER_ADDRESS, private_key=HERDMASTER_PRIVATE_KEY)
            if uid:
                existing_users.append(uid)
                print(f"Onboarded {uid}")
    
    staked_users = []
    for user_id in existing_users[:staked_target]:
        token_id = agent.users[user_id]["token_id"]
        if not process_novena(token_id, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY):
            print(f"Failed to process novena for {user_id}")
            return False
        staked_users.append(user_id)
    
    for user_id in staked_users:
        day = agent.users[user_id]["day"]
        for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
            msg = prompts[f"Day {day}"][prayer]
            agent.log_message(user_id, day, prayer, msg, silent=True)
        agent.record_response(user_id, day, "Compline", "y")
        agent.users[user_id]["day"] += 1
    
    agent.save_users()
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