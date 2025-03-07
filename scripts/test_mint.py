# scripts/test_mint.py
import requests
import json

BASE_URL = "https://stag-quest.vercel.app"

def test_mint(amount="0.001"):
    url = f"{BASE_URL}/api/mint?version=c"
    payload = {"amount": amount}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Mint Response: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    result = test_mint()