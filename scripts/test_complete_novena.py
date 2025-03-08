# scripts/test_complete_novena.py
import requests
import json

BASE_URL = "https://stag-quest.vercel.app"

def test_complete_novena(stag_id=2, successful_days=9):  # Changed to stagId=2
    url = f"{BASE_URL}/api/complete-novena?version=c"
    payload = {"stagId": stag_id, "successfulDays": successful_days}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Complete Novena Response: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    result = test_complete_novena()