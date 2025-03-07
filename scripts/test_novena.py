# scripts/test_novena.py
import requests
import json

BASE_URL = "https://stag-quest.vercel.app"

def test_start_novena(stag_id=1, amount="0.0005"):
    url = f"{BASE_URL}/api/novena?version=c"
    payload = {"stagId": stag_id, "amount": amount}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Start Novena Response: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    result = test_start_novena()