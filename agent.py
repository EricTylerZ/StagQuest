# agent.py
from config import w3, WALLET_ADDRESS, PRIVATE_KEY, CONTRACT_ADDRESS
from contract import mint_nft, stake_nft, resolve_day, get_nft_status
import json
from datetime import datetime

class StagAgent:
    def __init__(self):
        self.users = self.load_users()
        self.message_log = self.load_message_log()

    def load_users(self):
        try:
            with open("users.json") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"Error loading users.json: {e}")
            return {}

    def save_users(self):
        with open("users.json", "w") as f:
            json.dump(self.users, f, indent=4)

    def load_message_log(self):
        try:
            with open("message_log.json") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_message_log(self):
        with open("message_log.json", "w") as f:
            json.dump(self.message_log, f, indent=4)

    def onboard_user(self, signer_addr, fiat_amount, timezone_offset=-7, herdmaster_addr=None, private_key=None):
        if fiat_amount < 3.33:
            raise ValueError("Minimum $3.33 required!")
        if private_key is None:
            private_key = PRIVATE_KEY
        user_id = f"stag-{len(self.users) + 1}"
        tx_hash, token_id = mint_nft(signer_addr, private_key)
        if token_id is None:
            print("Failed to mint NFT. Aborting onboarding.")
            return None
        stake_nft(token_id, signer_addr, private_key)
        user_data = {
            "contract_address": CONTRACT_ADDRESS,
            "fiat_paid": fiat_amount,
            "timezone_offset": timezone_offset,
            "token_id": token_id,
            "day": 1,
            "mint_tx": tx_hash,
            "responses": {}
        }
        if herdmaster_addr:
            user_data["herdmaster"] = herdmaster_addr
        self.users[user_id] = user_data
        self.save_users()
        return user_id

    def log_message(self, user_id, day, prayer, msg):
        timestamp = datetime.now().isoformat()
        message_id = f"{user_id}|{day}|{prayer}"
        self.message_log[message_id] = {
            "timestamp": timestamp,
            "message": msg,
            "responded": False
        }
        self.save_message_log()
        print(f"Logged: {message_id} - {msg}")

    def record_response(self, user_id, day, prayer, response):
        message_id = f"{user_id}|{day}|{prayer}"
        if message_id in self.message_log:
            self.message_log[message_id]["responded"] = True
            self.message_log[message_id]["response"] = response
            self.save_message_log()
        user = self.users[user_id]
        token_id = user["token_id"]
        if prayer == "Compline":
            success = all(
                self.message_log[f"{user_id}|{day}|{p}"].get("response") == "y"
                for p in ["Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"]
            )
            resolve_day(token_id, success, WALLET_ADDRESS, PRIVATE_KEY)
            user["day"] += 1
            self.save_users()