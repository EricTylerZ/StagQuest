# main.py
from agent import StagAgent
from twilioSend import TwilioSender
import json

agent = StagAgent()
sender = TwilioSender()

# Onboard or load user
user_id = input("Enter user ID (e.g., stag-1): ")
if user_id not in agent.users:
    while True:
        phone = input("Enter phone number (e.g., +13035551234): ")
        if phone.startswith("+1") and len(phone) == 12 and phone[1:].isdigit():
            break
        print("Invalid US phone number! Use +1 followed by 10 digits (e.g., +13035551234)")
    while True:
        fiat_input = input("Name your price ($3.33+): ").strip().lstrip('$')
        try:
            fiat_amount = float(fiat_input)
            if fiat_amount >= 3.33:
                break
            print("Must be $3.33 or more!")
        except ValueError:
            print("Enter a valid number!")
    timezone_offset = -7  # Hardjammed MST
    user_id = agent.onboard_user(phone, fiat_amount, timezone_offset)
    print(f"User {user_id} onboarded!")
else:
    print(f"Loading user {user_id}")

# Schedule initial three days' texts (Saturday, Sunday, Monday)
with open("prompts.json") as f:
    prompts = json.load(f)

user = agent.users[user_id]
day = user["day"]
timezone_offset = user.get("timezone_offset", -7)  # Default to -7 if missing
if day > 9:
    print("Novena complete!")
elif day <= 3:
    sender.schedule_initial_days(user_id, user["phone"], prompts, timezone_offset)
    print(f"Scheduled 21 texts for Days 1-3 (Saturday, Sunday, Monday)!")
else:
    sender.schedule_day(user_id, user["phone"], day, prompts, timezone_offset)
    print(f"Scheduled 7 texts for Day {day}!")