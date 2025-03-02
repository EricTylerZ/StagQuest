# agent.py
from twilio.rest import Client
from config import w3, WALLET_ADDRESS, TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE
from contract import mint_nft, stake_eth, resolve_day, get_stake
import json

class StagAgent:
    def __init__(self):
        self.twilio = Client(TWILIO_SID, TWILIO_TOKEN)
        self.users = self.load_users()

    def load_users(self):
        try:
            with open("users.json") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(self):
        with open("users.json", "w") as f:
            json.dump(self.users, f, indent=4)

    def onboard_user(self, phone, fiat_amount, timezone_offset):
        if fiat_amount < 3.33:
            raise ValueError("Minimum $3.33 required!")
        user_id = f"stag-{len(self.users) + 1}"
        if get_stake() < 0.009:
            stake_eth()
        tx_hash, nft_id = mint_nft()
        self.users[user_id] = {
            "phone": phone,
            "fiat_paid": fiat_amount,
            "timezone_offset": timezone_offset,
            "nft_id": nft_id,
            "day": 1,
            "mint_tx": tx_hash
        }
        if fiat_amount > 20:
            print(f"High payer alert! {user_id} paid ${fiat_amount}")
        self.save_users()
        return user_id

    def send_prompt(self, user_id, day, prayer, msg, send_at=None):
        user = self.users[user_id]
        params = {
            "body": f"{user_id}|{day}|{prayer}: {msg}\nReply y/n",
            "from_": TWILIO_PHONE,
            "to": user["phone"]
        }
        if send_at:
            params["schedule_type"] = "fixed"
            params["send_at"] = send_at
        message = self.twilio.messages.create(**params)
        return message.sid

    def resolve_response(self, user_id, success):
        user = self.users[user_id]
        regen_addr = w3.to_checksum_address("0x2e0AA552E490Db6219C304a6b280e3DeA6962813")
        tx_hash = resolve_day(success, regen_addr)
        user["day"] += 1
        self.save_users()
        return tx_hash