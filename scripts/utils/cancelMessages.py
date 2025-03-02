# cancelMessages.py
from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN

def cancel_message(sid):
    """Cancel a scheduled Twilio message by its SID."""
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages(sid).update(status="canceled")
    print(f"Canceled message {sid}: New status = {message.status}")

if __name__ == "__main__":
    sid_to_cancel = input("Enter the Message SID to cancel (e.g., SMd9789d6086f3b8d318a925850185350e): ")
    cancel_message(sid_to_cancel)