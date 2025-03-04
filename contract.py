# contract.py
from config import w3, WALLET_ADDRESS, PRIVATE_KEY, CONTRACT_ADDRESS
import json

with open("abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
w3.eth.default_account = WALLET_ADDRESS

def mint_nft():
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    tx = contract.functions.mint().build_transaction({
        "from": WALLET_ADDRESS,
        "value": w3.to_wei(0.00009, "ether"),  # Updated to minMintFee
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    token_id = int(receipt["logs"][0]["topics"][2].hex(), 16)  # Extract token ID
    return tx_hash.hex(), token_id

def stake_nft(token_id, total_amount=0.00081, daily_amount=0.00009):
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    tx = contract.functions.stake(token_id, w3.to_wei(total_amount, "ether"), 
                                 w3.to_wei(daily_amount, "ether")).build_transaction({
        "from": WALLET_ADDRESS,
        "value": w3.to_wei(total_amount, "ether"),
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def resolve_day(token_id, success):
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    tx = contract.functions.resolveDay(token_id, success).build_transaction({
        "from": WALLET_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def get_nft_status(token_id):
    return {
        "days_completed": contract.functions.daysCompleted(token_id).call(),
        "successful_days": contract.functions.successfulDays(token_id).call(),
        "has_active_novena": contract.functions.hasActiveNovena(token_id).call(),
        "stake_remaining": w3.from_wei(contract.functions.stakes(token_id).call(), "ether")
    }