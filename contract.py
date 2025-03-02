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
        "value": w3.to_wei(0.001, "ether"),
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex(), receipt["logs"][0]["topics"][2].hex()  # NFT ID

def stake_eth(amount=0.009):
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    tx = contract.functions.stake().build_transaction({
        "from": WALLET_ADDRESS,
        "value": w3.to_wei(amount, "ether"),
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def resolve_day(success, regen_addr):
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
    tx = contract.functions.resolveDay(success, regen_addr).build_transaction({
        "from": WALLET_ADDRESS,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("2.5", "gwei")
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

def get_stake():
    return w3.from_wei(contract.functions.stakes(WALLET_ADDRESS).call(), "ether")