# scripts/test_transfer.py
import requests
import json

BASE_URL = "https://stag-quest.vercel.app"

def test_transfer(stag_id=1, to_address="0xYourTestAddress"):  # Replace with real address
    url = f"{BASE_URL}/api/transfer?version=c"
    payload = {"stagId": stag_id, "toAddress": to_address}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Transfer Response: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    result = test_transfer()