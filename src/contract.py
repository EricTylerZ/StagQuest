# src/contract.py
from src.config import w3, CONTRACT_ADDRESS
import json

with open("../data/abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

def mint_nft(signer_addr, private_key):
    try:
        nonce = w3.eth.get_transaction_count(signer_addr)
        tx = contract.functions.mint().build_transaction({
            "from": signer_addr,
            "value": w3.to_wei(0.00009, "ether"),
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 0:
            print(f"Transaction failed: {tx_hash.hex()}")
            return None, None
        
        for log in receipt["logs"]:
            if log["topics"][0] == w3.keccak(text="Transfer(address,address,uint256)"):
                token_id = int(log["topics"][3].hex(), 16)
                return tx_hash.hex(), token_id
        
        print("No Transfer event found.")
        return tx_hash.hex(), None
    
    except Exception as e:
        print(f"Error minting NFT: {str(e)}")
        return None, None

def stake_nft(token_id, signer_addr, private_key, total_amount=0.00081, daily_amount=0.00009):
    try:
        nonce = w3.eth.get_transaction_count(signer_addr)
        tx = contract.functions.stake(token_id, w3.to_wei(total_amount, "ether"), 
                                    w3.to_wei(daily_amount, "ether")).build_transaction({
            "from": signer_addr,
            "value": w3.to_wei(total_amount, "ether"),
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()
    except Exception as e:
        print(f"Error staking NFT: {str(e)}")
        return None

def resolve_day(token_id, success, signer_addr, private_key):
    try:
        nonce = w3.eth.get_transaction_count(signer_addr)
        tx = contract.functions.resolveDay(token_id, success).build_transaction({
            "from": signer_addr,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()
    except Exception as e:
        print(f"Error resolving day: {str(e)}")
        return None

def get_nft_status(token_id):
    try:
        return {
            "days_completed": contract.functions.daysCompleted(token_id).call(),
            "successful_days": contract.functions.successfulDays(token_id).call(),
            "has_active_novena": contract.functions.hasActiveNovena(token_id).call(),
            "stake_remaining": w3.from_wei(contract.functions.stakes(token_id).call(), "ether"),
            "daily_stake": w3.from_wei(contract.functions.dailyStakes(token_id).call(), "ether"),
            "owner": contract.functions.ownerOf(token_id).call()
        }
    except Exception as e:
        print(f"Error getting NFT status: {str(e)}")
        return None

def get_tokens_by_owner(owner_addr):
    try:
        balance = contract.functions.balanceOf(owner_addr).call()
        tokens = []
        for i in range(balance):
            token_id = contract.functions.tokenOfOwnerByIndex(owner_addr, i).call()
            tokens.append(token_id)
        return tokens
    except Exception as e:
        print(f"Error fetching tokens for {owner_addr}: {str(e)}")
        return []