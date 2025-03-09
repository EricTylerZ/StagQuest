# src/config.py
from dotenv import load_dotenv
import os
from web3 import Web3

load_dotenv()

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")  # Test user address
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Test user private key
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
TWILIO_MESSAGING_SID = os.getenv("TWILIO_MESSAGING_SID")
CONTRACT_ADDRESS = "0x5E1557B4C7Fc5268512E98662F23F923042FF5c5"  # Current StagQuest contract
RPC_URL = "https://sepolia.base.org"
OWNER_ADDRESS = os.getenv("OWNER_ADDRESS")  # Contract owner
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")  # Contract owner private key

w3 = Web3(Web3.HTTPProvider(RPC_URL))