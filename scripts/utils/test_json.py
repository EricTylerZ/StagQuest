# test_json.py
import json
with open("users.json", "r") as f:
    print(json.load(f))