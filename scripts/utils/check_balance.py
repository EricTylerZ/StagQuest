# check_balance.py
from config import w3, WALLET_ADDRESS, HERDMASTER_ADDRESS, OWNER_ADDRESS
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def check_balance(addr):
    balance = w3.from_wei(w3.eth.get_balance(addr), "ether")
    print(f"Balance for {addr}: {balance} ETH")

if __name__ == "__main__":
    check_balance(WALLET_ADDRESS)
    check_balance(HERDMASTER_ADDRESS)
    check_balance(OWNER_ADDRESS)