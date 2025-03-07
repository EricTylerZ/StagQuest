#!/usr/bin/env python3
# view_message_status.py
import json
import os

def view_message_status(user_id, log_file="message_log.json"):
    if not os.path.exists(log_file):
        print(f"Error: '{log_file}' not found. Please ensure the message log exists.")
        return
    
    try:
        with open(log_file, "r") as f:
            message_log = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: '{log_file}' is not a valid JSON file.")
        return
    
    print(f"\nMessage status for '{user_id}':")
    found = False
    for key, data in message_log.items():
        if key.startswith(user_id):
            print(f"  {key}: {data}")
            found = True
    if not found:
        print(f"  No messages found for '{user_id}'.")

if __name__ == "__main__":
    user_id = input("Enter user ID (e.g., stag-2): ").strip()
    view_message_status(user_id)