# src/utils.py
import requests
from web3 import Web3

CONTRACT_ADDRESS = "0x70bbAB9B860725A3f817dF4bCCB0C6edB2C4DcF8"

def get_stake_tx(token_id):
    """Fetch staking tx hash and ETH value for a token_id from Blockscout API."""
    try:
        url = f"https://base-sepolia.blockscout.com/api?module=account&action=txlist&address={CONTRACT_ADDRESS}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Blockscout API error: {response.status_code}")
            return "unknown", 0.0

        txs = response.json().get("result", [])
        stake_method_id = "0x3a4b66f1"  # Method ID for stake()

        for tx in txs:
            if (tx["to"].lower() == CONTRACT_ADDRESS.lower() and 
                tx["input"].startswith(stake_method_id) and 
                int(tx["isError"]) == 0):  # Only successful txs
                # Decode input: stake(uint256 tokenId, uint256 totalAmount, uint256 dailyAmount)
                input_data = tx["input"][10:]  # Skip method ID
                token_id_input = int(input_data[:64], 16)  # First 32 bytes
                if token_id_input == token_id:
                    eth_value = Web3.from_wei(int(tx["value"]), "ether")
                    return tx["hash"], float(eth_value)
        print(f"No staking tx found for token {token_id}")
        return "unknown", 0.0
    except Exception as e:
        print(f"Error fetching stake tx for token {token_id}: {e}")
        return "unknown", 0.0