# test_utils.py
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from agent import StagAgent
from config import WALLET_ADDRESS, PRIVATE_KEY, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY

agent = StagAgent()

with open(os.path.join(os.path.dirname(__file__), '..', '..', 'prompts.json')) as f:
    prompts = json.load(f)

def onboard_test_users(signer_addr, private_key, num_users=1, herdmaster_addr=None):
    user_ids = []
    existing_users = [uid for uid, u in agent.users.items() if u.get("owner") == signer_addr and (herdmaster_addr is None or u.get("herdmaster") == herdmaster_addr)]
    if existing_users and not herdmaster_addr:
        print(f"Address {signer_addr} already has NFT(s): {existing_users}. Using existing user instead of minting.")
        return existing_users[:1]
    elif existing_users and herdmaster_addr:
        print(f"Address {signer_addr} already has NFT(s): {existing_users}. Adding more.")
    for _ in range(num_users - len(existing_users)):
        uid = agent.onboard_user(signer_addr, 3.33, timezone_offset=-7, herdmaster_addr=herdmaster_addr, private_key=private_key)
        if uid:
            user_ids.append(uid)
            role = "herdmaster" if herdmaster_addr else "individual"
            print(f"Onboarded user {uid} as {role} with signer {signer_addr}")
    return existing_users + user_ids

def log_daily_messages(user_id):
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
    user = agent.users[user_id]
    day = user["day"]
    for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers"]:
        agent.record_response(user_id, day, prayer, None)
    agent.record_response(user_id, day, "Compline", response)
    print(f"Recorded response '{response}' for {user_id}, Day {day}, Compline")
    if user["day"] > day:
        print(f"{user_id} has advanced to day {user['day']}")

def run_test(signer_addr, private_key, num_users=1, herdmaster_addr=None, response="y"):
    user_ids = onboard_test_users(signer_addr, private_key, num_users, herdmaster_addr)
    for user_id in user_ids:
        log_daily_messages(user_id)
        simulate_responses(user_id, response)

if __name__ == "__main__":
    test_type = input("Test as herdmaster (h) or individual (i)? ").lower()
    if test_type == "h":
        signer_addr = HERDMASTER_ADDRESS
        private_key = HERDMASTER_PRIVATE_KEY
        num_users = 3
        print(f"Testing herdmaster with address {signer_addr}")
        run_test(signer_addr, private_key, num_users, herdmaster_addr=signer_addr)
    elif test_type == "i":
        signer_addr = WALLET_ADDRESS
        private_key = PRIVATE_KEY
        print(f"Testing individual with address {signer_addr}")
        run_test(signer_addr, private_key, num_users=1)
    else:
        print("Invalid choice. Use 'h' for herdmaster or 'i' for individual.")