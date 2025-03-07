#webhook.py
from flask import Flask, request
from agent import StagAgent

app = Flask(__name__)
agent = StagAgent()

@app.route("/twilio", methods=["POST"])
def twilio_reply():
    msg = request.values.get("Body", "").strip()
    user_id, day, _ = msg.split("|", 2)  # Parse "stag-1|1|Lauds: ..."
    success = msg.endswith("y")
    tx_hash = agent.resolve_response(user_id, success)
    return f"Resolved: {tx_hash}"

if __name__ == "__main__":
    app.run(port=5000)