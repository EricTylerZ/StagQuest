# scripts/test_batch_complete.py
import requests
import json

BASE_URL = "https://stag-quest.vercel.app"

def test_batch_complete(stag_ids=[1, 2], successful_days=[9, 7]):
    url = f"{BASE_URL}/api/batch-complete-novena?version=c"
    payload = {"stagIds": stag_ids, "successfulDays": successful_days}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Batch Complete Response: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    result = test_batch_complete()