# test_utils.py
import sys
import os
import json

# Adjust the path to import StagAgent from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent import StagAgent

# Initialize the agent
agent = StagAgent()

# Load prompts
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'prompts.json')) as f:
    prompts = json.load(f)

def onboard_test_users(herdmaster_addr, num_users=3, fiat_amount=3.33):
    """Onboard multiple test users and mint NFTs."""
    for _ in range(num_users):
        user_id = agent.onboard_user(herdmaster_addr, fiat_amount)
        print(f"Onboarded user {user_id} for herdmaster {herdmaster_addr}")
    return [uid for uid in agent.users if agent.users[uid]["herdmaster"] == herdmaster_addr]

def log_daily_messages(user_id):
    """Log the 7 daily messages for a user's current day."""
    user = agent.users[user_id]
    day = user["day"]
    if day > 9:
        print(f"{user_id}: Novena complete!")
        return
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        msg = prompts[f"Day {day}"][prayer]
        agent.log_message(user_id, day, prayer, msg)
        print(f"Logged message for {user_id}, Day {day}, {prayer}")

def simulate_responses(user_id, response="y"):
    """Simulate responses for all 7 messages of a user's current day."""
    user = agent.users[user_id]
    day = user["day"]
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
        agent.record_response(user_id, day, prayer, response)
        print(f"Recorded response '{response}' for {user_id}, Day {day}, {prayer}")

def run_test(herdmaster_addr, num_users=3, response="y"):
    """Run a full test: onboard users, log messages, simulate responses."""
    # Onboard users and get their IDs
    user_ids = onboard_test_users(herdmaster_addr, num_users)
    
    # Process each user
    for user_id in user_ids:
        log_daily_messages(user_id)        # Queue up messages
        simulate_responses(user_id, response)  # Simulate responses
        
        # Check if the day advanced
        user = agent.users[user_id]
        if user["day"] > 1:
            print(f"{user_id} has advanced to day {user['day']}")

if __name__ == "__main__":
    herdmaster_addr = input("Enter your herdmaster address: ")
    run_test(herdmaster_addr)