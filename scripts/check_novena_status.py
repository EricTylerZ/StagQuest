# scripts/check_novena_status.py (updated)
import requests
import json
import subprocess
import time

BASE_URL = "https://stag-quest.vercel.app/api"

def fetch_status(version):
    response = requests.get(f"{BASE_URL}/status?version={version}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch status for version {version}: {response.status_code}")
        return {"stags": []}

def suggest_action(stag_a, stag_b):
    actions = []
    stag_id = stag_a["tokenId"]
    
    if not stag_a["hasActiveNovena"] and stag_b["hasActiveNovena"]:
        actions.append({
            "command": f"Invoke-RestMethod -Uri '{BASE_URL}/novena?version=a' -Method Post -Body (@{{ stagId = {stag_id} }} | ConvertTo-Json) -ContentType 'application/json'",
            "description": f"Start novena for Stag {stag_id} on Version A"
        })
    elif stag_a["hasActiveNovena"] and not stag_b["hasActiveNovena"]:
        actions.append({
            "command": f"Invoke-RestMethod -Uri '{BASE_URL}/novena?version=b' -Method Post -Body (@{{ stagId = {stag_id} }} | ConvertTo-Json) -ContentType 'application/json'",
            "description": f"Start novena for Stag {stag_id} on Version B"
        })
    
    if stag_a["hasActiveNovena"] and stag_b["hasActiveNovena"]:
        diff = stag_b["daysCompleted"] - stag_a["daysCompleted"]
        if diff > 0:
            for _ in range(diff):
                actions.append({
                    "command": f"Invoke-RestMethod -Uri '{BASE_URL}/checkin?version=a' -Method Post -Body (@{{ stagId = {stag_id} }} | ConvertTo-Json) -ContentType 'application/json'",
                    "description": f"Check in Stag {stag_id} on Version A"
                })
        elif diff < 0:
            for _ in range(-diff):
                actions.append({
                    "command": f"Invoke-RestMethod -Uri '{BASE_URL}/checkin?version=b' -Method Post -Body (@{{ stagId = {stag_id} }} | ConvertTo-Json) -ContentType 'application/json'",
                    "description": f"Check in Stag {stag_id} on Version B"
                })
    
    # Complete novenas if aligned
    if stag_a["hasActiveNovena"] and stag_b["hasActiveNovena"] and stag_a["daysCompleted"] == stag_b["daysCompleted"]:
        remaining = 9 - stag_a["daysCompleted"]
        for _ in range(remaining):
            actions.append({
                "command": f"Invoke-RestMethod -Uri '{BASE_URL}/checkin?version=a' -Method Post -Body (@{{ stagId = {stag_id} }} | ConvertTo-Json) -ContentType 'application/json'",
                "description": f"Check in Stag {stag_id} on Version A (to complete)"
            })
            actions.append({
                "command": f"Invoke-RestMethod -Uri '{BASE_URL}/checkin?version=b' -Method Post -Body (@{{ stagId = {stag_id} }} | ConvertTo-Json) -ContentType 'application/json'",
                "description": f"Check in Stag {stag_id} on Version B (to complete)"
            })
    
    return actions

def withdraw(version, stag_id):
    body = json.dumps({"userAddress": "0x2e0AA552E490Db6219C304a6b280e3DeA6962813"})
    result = subprocess.run([
        "powershell",
        "-Command",
        f"Invoke-RestMethod -Uri '{BASE_URL}/user-withdraw?version={version}' -Method Post -Body '{body}' -ContentType 'application/json'"
    ], capture_output=True, text=True, shell=True)
    print(f"Withdraw Version {version} for Stag {stag_id}:")
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")

def main():
    status_a = fetch_status("a")
    status_b = fetch_status("b")
    
    print(f"Version A Stags: {len(status_a['stags'])}")
    print(f"Version B Stags: {len(status_b['stags'])}")
    print("\nNovena Status Comparison:")
    
    actions_queue = []
    for stag_a, stag_b in zip(status_a["stags"], status_b["stags"]):
        print(f"Stag {stag_a['tokenId']}:")
        print(f"  A: Active={stag_a['hasActiveNovena']}, DaysCompleted={stag_a['daysCompleted']}, SuccessfulDays={stag_a['successfulDays']}")
        print(f"  B: Active={stag_b['hasActiveNovena']}, DaysCompleted={stag_b['daysCompleted']}, SuccessfulDays={stag_b['successfulDays']}")
        
        if (stag_a["hasActiveNovena"] != stag_b["hasActiveNovena"] or
            stag_a["daysCompleted"] != stag_b["daysCompleted"] or
            stag_a["successfulDays"] != stag_b["successfulDays"] or
            (stag_a["hasActiveNovena"] and stag_a["daysCompleted"] < 9)):
            print("  (DIFFERENT or INCOMPLETE)")
            actions = suggest_action(stag_a, stag_b)
            actions_queue.extend(actions)
    
    if actions_queue:
        print("\nSuggested Actions to Align and Complete Novenas:")
        for i, action in enumerate(actions_queue, 1):
            print(f"{i}. {action['description']}")
        
        while True:
            confirm = input("\nDo you want to execute these commands? (yes/y/no): ").lower()
            if confirm in ["yes", "y"]:
                for action in actions_queue:
                    print(f"Executing: {action['description']}")
                    subprocess.run(["powershell", "-Command", action["command"]], shell=True)
                    time.sleep(10)
                # Withdraw after completion
                for stag_a in status_a["stags"]:
                    if not stag_a["hasActiveNovena"]:
                        withdraw("a", stag_a["tokenId"])
                for stag_b in status_b["stags"]:
                    if not stag_b["hasActiveNovena"]:
                        withdraw("b", stag_b["tokenId"])
                print("\nRe-checking status:")
                main()
                break
            elif confirm == "no":
                print("No actions executed.")
                break
            else:
                print("Invalid input. Please enter 'yes', 'y', or 'no'.")
    else:
        print("\nNo differences or incomplete novenas—statuses aligned and completed.")

if __name__ == "__main__":
    main()