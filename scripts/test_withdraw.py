# scripts/test_withdraw.py
import requests
import json

BASE_URL = "https://stag-quest.vercel.app"

def test_withdraw():
    url = f"{BASE_URL}/api/owner-withdraw?version=c"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers)
    print(f"Withdraw Response: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    result = test_withdraw()