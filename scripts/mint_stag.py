# scripts/mint_stag.py
import os
import sys
# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web3 import Web3
from src.config import w3, CONTRACT_ADDRESS, OWNER_ADDRESS, OWNER_PRIVATE_KEY

# Load ABI from GitHub
import requests
ABI_URL = "https://raw.githubusercontent.com/EricTylerZ/StagQuest/main/data/abi.json"

def load_json_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Failed to load {url}: Status {response.status_code}")

abi = load_json_from_url(ABI_URL)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def mint_stag():
    try:
        nonce = w3.eth.get_transaction_count(OWNER_ADDRESS)
        mint_fee = w3.to_wei("0.0001", "ether")  # Matches minMintFee
        tx = contract.functions.mintStag().build_transaction({
            "from": OWNER_ADDRESS,
            "value": mint_fee,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei"),
            "chainId": 84532  # Base Sepolia
        })
        signed_tx = w3.eth.account.sign_transaction(tx, OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print(f"Successfully minted Stag with tx: {tx_hash.hex()}")
            # Get tokenId from Transfer event
            for log in receipt["logs"]:
                if log["topics"][0].hex() == w3.keccak(text="Transfer(address,address,uint256)").hex():
                    token_id = int(log["topics"][3].hex(), 16)
                    print(f"Minted Stag ID: {token_id}")
                    return token_id
            return None
        else:
            print(f"Minting failed with tx: {tx_hash.hex()}")
            return None
    except Exception as e:
        print(f"Error minting Stag: {e}")
        return None

if __name__ == "__main__":
    token_id = mint_stag()
    if token_id:
        print(f"Use this stagId for testing: {token_id}")