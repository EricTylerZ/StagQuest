# src/utils.py
import requests
from web3 import Web3
from src.config import CONTRACT_ADDRESS

def get_stake_tx(token_id):
    """Fetch staking tx hash and ETH value for a token_id from Blockscout API."""
    try:
        page = 1
        txs = []
        while True:
            url = f"https://base-sepolia.blockscout.com/api?module=account&action=txlist&address={CONTRACT_ADDRESS}&page={page}&offset=1000"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Blockscout API error on page {page}: {response.status_code}")
                break
            data = response.json().get("result", [])
            if not data:
                break
            txs.extend(data)
            page += 1

        stake_method_id = "0x3a4b66f1"  # Method ID for stake()
        for tx in txs:
            if (tx["to"].lower() == CONTRACT_ADDRESS.lower() and 
                tx["input"].startswith(stake_method_id) and 
                int(tx["isError"]) == 0):
                input_data = tx["input"][10:]
                token_id_input = int(input_data[:64], 16)
                if token_id_input == token_id:
                    eth_value = Web3.from_wei(int(tx["value"]), "ether")
                    return tx["hash"], float(eth_value)
        print(f"No staking tx found for token {token_id}")
        return "unknown", 0.0
    except Exception as e:
        print(f"Error fetching stake tx for token {token_id}: {e}")
        return "unknown", 0.0

def get_mint_tx(token_id):
    """Fetch minting tx hash from Blockscout API."""
    try:
        page = 1
        txs = []
        while True:
            url = f"https://base-sepolia.blockscout.com/api?module=account&action=tokenlist&address={CONTRACT_ADDRESS}&page={page}&offset=1000"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Blockscout API error on page {page}: {response.status_code}")
                break
            data = response.json().get("result", [])
            if not data:
                break
            txs.extend(data)
            page += 1

        for tx in txs:
            if int(tx["tokenID"]) == token_id:
                return tx["transactionHash"]
        print(f"No mint tx found for token {token_id}")
        return "unknown"
    except Exception as e:
        print(f"Error fetching mint tx for token {token_id}: {e}")
        return "unknown"