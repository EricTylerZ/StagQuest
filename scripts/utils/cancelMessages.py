# cancelMessages.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN

def cancel_message(client, sid):
    """Cancel a scheduled Twilio message by its SID."""
    try:
        message = client.messages(sid).update(status="canceled")
        print(f"Canceled message {sid}: New status = {message.status}")
    except Exception as e:
        print(f"Failed to cancel {sid}: {str(e)}")

if __name__ == "__main__":
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    if len(sys.argv) < 2:
        print("Usage: python cancelMessages.py SID1 [SID2 SID3 ...]")
        print("Example: python cancelMessages.py SMd9789d6086f3b8d318a925850185350e SM6f40e7892d01002ceca9d7d2d76cd286")
        sys.exit(1)
    
    sids_to_cancel = sys.argv[1:]
    for sid in sids_to_cancel:
        cancel_message(client, sid)