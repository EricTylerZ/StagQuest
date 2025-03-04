# config.py
from dotenv import load_dotenv
import os
from web3 import Web3

load_dotenv()

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
TWILIO_MESSAGING_SID = os.getenv("TWILIO_MESSAGING_SID")
CONTRACT_ADDRESS = "0x70bbAB9B860725A3f817dF4bCCB0C6edB2C4DcF8"  # Updated to match deployment
OLD_CONTRACT_ADDRESS_1 = "0xfE745e106CF1C837b3A0e39f0528B2e67be8f9c4"  # Old address moved here
RPC_URL = "https://sepolia.base.org"
HERDMASTER_ADDRESS = os.getenv("HERDMASTER_ADDRESS")
HERDMASTER_PRIVATE_KEY = os.getenv("HERDMASTER_PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(RPC_URL))