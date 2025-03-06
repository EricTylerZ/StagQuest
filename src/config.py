# src/config.py
from dotenv import load_dotenv
import os
from web3 import Web3

load_dotenv()

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")  # Test for Individual user (0xbae9b7...)
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Test for Individual key
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
TWILIO_MESSAGING_SID = os.getenv("TWILIO_MESSAGING_SID")
CONTRACT_ADDRESS = "0x235c9b74A583b0b79CA3d32E31199528fBc906Da"  # New StagQuest
NOVENA_PROCESSOR_ADDRESS = "0x33ce117015a834D2631d72f4Fe13C26366E5F5BA"  # NovenaProcessor, now unnecessary
OLD_CONTRACT_ADDRESS_1 = "0xF58C871e0D185C9878E3b96Fb0016665Aa915223"  # Old StagQuest
RPC_URL = "https://sepolia.base.org"
ORACLE_ADDRESS = os.getenv("ORACLE_ADDRESS")  # Oracle wallet address
ORACLE_PRIVATE_KEY = os.getenv("ORACLE_PRIVATE_KEY")  # Oracle private key
OWNER_ADDRESS = os.getenv("OWNER_ADDRESS")  # Contract owner (likely 0x2e0AA552...)
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(RPC_URL))