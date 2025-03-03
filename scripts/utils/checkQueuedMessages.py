# checkQueuedMessages.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN

def check_queued_messages():
    """List all queued/scheduled messages in Twilio account via API."""
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        messages = client.messages.list()
        queued_messages = [msg for msg in messages if msg.status in ["queued", "scheduled"]]
        
        if not queued_messages:
            print("No queued/scheduled messages found.")
            return
            
        for msg in queued_messages:
            scheduled_time = msg.date_sent if msg.status == 'sent' else msg.date_created
            print(f"SID: {msg.sid}, To: {msg.to}, Scheduled: {scheduled_time}, Status: {msg.status}, Body: {msg.body[:60]}...")
            
    except Exception as e:
        print(f"Error checking messages: {str(e)}")

if __name__ == "__main__":
    check_queued_messages()