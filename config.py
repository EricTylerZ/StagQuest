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
CONTRACT_ADDRESS = "0x70bbAB9B860725A3f817dF4bCCB0C6edB2C4DcF8"
RPC_URL = "https://sepolia.base.org"

w3 = Web3(Web3.HTTPProvider(RPC_URL))