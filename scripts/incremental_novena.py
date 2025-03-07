# scripts/incremental_novena.py
import requests
import json
import subprocess
import time

BASE_URL = "https://stag-quest.vercel.app/api"

def checkin(version, stag_id, days_to_do):
    body = json.dumps({"stagId": stag_id})
    for day in range(days_to_do):
        print(f"Checking in Stag {stag_id} on Version {version}, Day {day + 1}/{days_to_do}")
        result = subprocess.run([
            "powershell",
            "-Command",
            f"Invoke-RestMethod -Uri '{BASE_URL}/checkin?version={version}' -Method Post -Body '{body}' -ContentType 'application/json'"
        ], capture_output=True, text=True, shell=True)
        print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
            return False
        time.sleep(10)  # Wait for tx confirmation
    return True

def withdraw(version, user_address):
    body = json.dumps({"userAddress": user_address})
    result = subprocess.run([
        "powershell",
        "-Command",
        f"Invoke-RestMethod -Uri '{BASE_URL}/user-withdraw?version={version}' -Method Post -Body '{body}' -ContentType 'application/json'"
    ], capture_output=True, text=True, shell=True)
    print(f"Withdraw on Version {version}:")
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
        return False
    return True

def main():
    # Version A: Stag 1, 7 days total, 3 then withdraw, 4 more
    if checkin("a", 1, 3):  # Days 3-5
        print("3 check-ins completed on Version A.")
    withdraw("a", "0x2e0AA552E490Db6219C304a6b280e3DeA6962813")
    if checkin("a", 1, 4):  # Days 6-9
        print("Stag 1 novena on Version A completed.")
    withdraw("a", "0x2e0AA552E490Db6219C304a6b280e3DeA6962813")

    # Version B: Stag 1, 8 days total, 3 then withdraw, repeat
    if checkin("b", 1, 3):  # Days 2-4
        print("3 check-ins completed on Version B.")
    withdraw("b", "0x2e0AA552E490Db6219C304a6b280e3DeA6962813")
    if checkin("b", 1, 3):  # Days 5-7
        print("3 more check-ins completed on Version B.")
    withdraw("b", "0x2e0AA552E490Db6219C304a6b280e3DeA6962813")
    if checkin("b", 1, 2):  # Days 8-9
        print("Stag 1 novena on Version B completed.")
    withdraw("b", "0x2e0AA552E490Db6219C304a6b280e3DeA6962813")

if __name__ == "__main__":
    main()