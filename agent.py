# agent.py
from config import w3, WALLET_ADDRESS, PRIVATE_KEY, CONTRACT_ADDRESS, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY, OWNER_ADDRESS, OWNER_PRIVATE_KEY
from contract import mint_nft, stake_nft, resolve_day, get_nft_status, get_tokens_by_owner
import json
from datetime import datetime

class StagAgent:
    def __init__(self):
        self.users = self.load_users()
        self.message_log = self.load_message_log()
        self.sync_with_contract()

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

    def sync_with_contract(self):
        for addr in [WALLET_ADDRESS, HERDMASTER_ADDRESS]:
            token_ids = get_tokens_by_owner(addr)
            for token_id in token_ids:
                status = get_nft_status(token_id)
                if status:
                    user_id = None
                    for uid, data in self.users.items():
                        if data.get("token_id") == token_id:
                            user_id = uid
                            break
                    if not user_id:
                        i = 2
                        while f"stag-{i}" in self.users:
                            i += 1
                        user_id = f"stag-{i}"
                    user_data = self.users.get(user_id, {})
                    user_data.update({
                        "contract_address": CONTRACT_ADDRESS,
                        "owner": status["owner"],
                        "token_id": token_id,
                        "day": status["days_completed"] + 1 if status["has_active_novena"] else 10,
                        "responses": user_data.get("responses", {})
                    })
                    if addr == HERDMASTER_ADDRESS and "herdmaster" not in user_data:
                        user_data["herdmaster"] = HERDMASTER_ADDRESS
                    user_data.setdefault("fiat_paid", 3.33)
                    user_data.setdefault("timezone_offset", -7)
                    user_data.setdefault("mint_tx", "unknown")
                    self.users[user_id] = user_data
        self.save_users()

    def onboard_user(self, signer_addr, fiat_amount, timezone_offset=-7, herdmaster_addr=None, private_key=None):
        if fiat_amount < 3.33:
            raise ValueError("Minimum $3.33 required!")
        if private_key is None:
            private_key = PRIVATE_KEY
        i = 2
        while f"stag-{i}" in self.users:
            i += 1
        user_id = f"stag-{i}"
        tx_hash, token_id = mint_nft(signer_addr, private_key)
        if token_id is None:
            print("Failed to mint NFT. Aborting onboarding.")
            return None
        stake_nft(token_id, signer_addr, private_key)
        user_data = {
            "contract_address": CONTRACT_ADDRESS,
            "owner": signer_addr,
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
            if response is not None:
                self.message_log[message_id]["responded"] = True
                self.message_log[message_id]["response"] = response
            self.save_message_log()
        user = self.users[user_id]
        token_id = user["token_id"]
        if prayer == "Compline" and response is not None:
            success = response.lower() == "y"
            resolve_day(token_id, success, OWNER_ADDRESS, OWNER_PRIVATE_KEY)  # Use owner credentials
            user["day"] += 1
            self.save_users()