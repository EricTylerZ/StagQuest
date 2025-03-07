# scripts/mint_helper.py
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import w3, CONTRACT_ADDRESS, WALLET_ADDRESS, PRIVATE_KEY, HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY

with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'abi.json'), 'r') as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def mint_nft(address, private_key, value=0.00009):
    """Mint an NFT for the given address."""
    try:
        nonce = w3.eth.get_transaction_count(address)
        tx = contract.functions.mint().build_transaction({
            "from": address,
            "value": w3.to_wei(value, "ether"),
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Minting failed: {tx_hash.hex()}")
            return None, None
        
        for log in receipt["logs"]:
            if log["topics"][0] == w3.keccak(text="Transfer(address,address,uint256)"):
                token_id = int(log["topics"][3].hex(), 16)
                print(f"Minted NFT with tx: {tx_hash.hex()}, token_id: {token_id}")
                return tx_hash.hex(), token_id
        
        print(f"No Transfer event found: {tx_hash.hex()}")
        return tx_hash.hex(), None
    except Exception as e:
        print(f"Error minting NFT: {e}")
        return None, None

if __name__ == "__main__":
    print("Minting for individual...")
    mint_nft(WALLET_ADDRESS, PRIVATE_KEY)
    print("Minting for herdmaster...")
    mint_nft(HERDMASTER_ADDRESS, HERDMASTER_PRIVATE_KEY)