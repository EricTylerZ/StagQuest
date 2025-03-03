# checkQueuedMessages.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN

def check_queued_messages():
    """List all queued messages in Twilio account via API."""
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    messages = client.messages.list(status="queued")
    if not messages:
        print("No queued messages found.")
        return
    
    for msg in messages:
        print(f"SID: {msg.sid}, To: {msg.to}, SendAt: {msg.send_at}, Status: {msg.status}, Body: {msg.body}")

if __name__ == "__main__":
    check_queued_messages()