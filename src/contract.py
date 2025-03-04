# src/contract.py
import os
import json
from src.config import w3, CONTRACT_ADDRESS, WALLET_ADDRESS, HERDMASTER_ADDRESS
from web3 import Web3

NOVENA_PROCESSOR_ADDRESS = "0x630E91fAB353b87357E022f5422C29D7c0c95D41"

# Load ABIs
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
with open(os.path.join(data_dir, 'abi.json'), 'r') as f:
    contract_abi = json.load(f)
with open(os.path.join(data_dir, 'novena_abi.json'), 'r') as f:
    novena_abi = json.load(f)

stag_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
novena_contract = w3.eth.contract(address=NOVENA_PROCESSOR_ADDRESS, abi=novena_abi)

def mint_nft(signer_addr, private_key):
    """Mint an NFT via StagQuest (not used here, kept for reference)."""
    try:
        nonce = w3.eth.get_transaction_count(signer_addr)
        tx = stag_contract.functions.mint().build_transaction({
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
        print(f"Error minting NFT: {e}")
        return None, None

def stake_nft(token_id, signer_addr, private_key, total_amount=0.00081, daily_amount=0.00009):
    """Stake an NFT via NovenaProcessor."""
    try:
        nonce = w3.eth.get_transaction_count(signer_addr)
        tx = novena_contract.functions.stake(token_id, w3.to_wei(total_amount, "ether"), 
                                    w3.to_wei(daily_amount, "ether")).build_transaction({
            "from": signer_addr,
            "value": w3.to_wei(total_amount, "ether"),
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Staking failed: {tx_hash.hex()}")
            return None
        return tx_hash.hex()
    except Exception as e:
        print(f"Error staking NFT: {e}")
        return None

def resolve_day(token_id, success, signer_addr, private_key):
    """Resolve a day via NovenaProcessor."""
    try:
        nonce = w3.eth.get_transaction_count(signer_addr)
        tx = novena_contract.functions.resolveDay(token_id, success).build_transaction({
            "from": signer_addr,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("2.5", "gwei")
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 0:
            print(f"Resolve day failed: {tx_hash.hex()}")
            return None
        return tx_hash.hex()
    except Exception as e:
        print(f"Error resolving day: {e}")
        return None

def get_nft_status(token_id):
    """Get NFT status from NovenaProcessor."""
    try:
        status = novena_contract.functions.daysCompleted(token_id).call()
        successful_days = novena_contract.functions.successfulDays(token_id).call()
        has_active = novena_contract.functions.hasActiveNovena(token_id).call()
        stake = novena_contract.functions.stakes(token_id).call()
        daily = novena_contract.functions.dailyStakes(token_id).call()
        owner = stag_contract.functions.ownerOf(token_id).call()
        return {
            "days_completed": status,
            "successful_days": successful_days,
            "has_active_novena": has_active,
            "stake_remaining": w3.from_wei(stake, "ether"),
            "daily_stake": w3.from_wei(daily, "ether"),
            "owner": owner
        }
    except Exception as e:
        print(f"Error getting NFT status: {e}")
        return None

def get_tokens_by_owner(owner_addr):
    """Get token IDs owned by an address via StagQuest."""
    try:
        balance = stag_contract.functions.balanceOf(owner_addr).call()
        tokens = []
        for i in range(balance):
            token_id = stag_contract.functions.tokenOfOwnerByIndex(owner_addr, i).call()
            tokens.append(token_id)
        return tokens
    except Exception as e:
        print(f"Error fetching tokens for {owner_addr}: {e}")
        return []