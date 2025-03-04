# main.py
from agent import StagAgent
from datetime import datetime
import json

agent = StagAgent()

def manage_nfts(herdmaster_addr):
    print(f"Herdmaster: {herdmaster_addr}")
    herd_nfts = {uid: u for uid, u in agent.users.items() if u["herdmaster"] == herdmaster_addr}
    if not herd_nfts:
        print("No NFTs assigned. Onboard a user?")
        if input("Yes/No: ").lower() == "y":
            fiat = float(input("Fiat amount ($3.33+): "))
            user_id = agent.onboard_user(herdmaster_addr, fiat)
            print(f"Onboarded {user_id}")
            herd_nfts[user_id] = agent.users[user_id]

    with open("prompts.json") as f:
        prompts = json.load(f)

    for user_id, user in herd_nfts.items():
        token_id = user["token_id"]
        day = user["day"]
        if day > 9:
            print(f"{user_id} (Token {token_id}): Novena complete!")
            continue
        print(f"Processing {user_id} (Token {token_id}) - Day {day}")
        for prayer in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]:
            msg = prompts[f"Day {day}"][prayer]
            agent.log_message(user_id, day, prayer, msg)
            # Simulate response for testing
            response = input(f"{user_id}|{day}|{prayer}: {msg}\nReply y/n: ")
            agent.record_response(user_id, day, prayer, response)

if __name__ == "__main__":
    herdmaster_addr = input("Enter your herdmaster address: ")
    manage_nfts(herdmaster_addr)