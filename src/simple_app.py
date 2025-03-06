# src/simple_app.py
from flask import Flask

app = Flask(__name__)

@app.route("/api/checkin", methods=["POST"])
def checkin():
    return {"message": "Check-in successful"}, 200

@app.route("/", methods=["GET"])
def home():
    return "Welcome to StagQuest API", 200

if __name__ == "__main__":
    app.run()