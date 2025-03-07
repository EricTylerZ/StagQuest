# scripts/test_status.py
import requests
import json

BASE_URL = "https://stag-quest.vercel.app"

def test_status():
    url = f"{BASE_URL}/api/status?version=c"
    response = requests.get(url)
    print(f"Status Response: {response.status_code} - {response.text}")
    return response.json()

if __name__ == "__main__":
    result = test_status()