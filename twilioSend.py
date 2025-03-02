# twilioSend.py
from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN, TWILIO_MESSAGING_SID
from datetime import datetime, timedelta

class TwilioSender:
    def __init__(self):
        self.client = Client(TWILIO_SID, TWILIO_TOKEN)

    def schedule_day(self, user_id, phone, day, prompts, timezone_offset):
        offset = timedelta(hours=timezone_offset)
        now_utc = datetime.utcnow()
        local_now = now_utc + offset
        # Start scheduling from tomorrow morning
        tomorrow = local_now.date() + timedelta(days=1)
        day_date = tomorrow + timedelta(days=day-1)  # Day 1 = tomorrow
        prayer_times = {
            "Lauds": 6, "Prime": 7, "Terce": 9, "Sext": 12, "None": 15,
            "Vespers": 18, "Compline": 21
        }
        for prayer, hour in prayer_times.items():
            local_send_time = datetime(day_date.year, day_date.month, day_date.day, hour, 0)
            utc_send_time = local_send_time - offset
            send_at = utc_send_time.isoformat() + "Z"
            msg = prompts[f"Day {day}"][prayer]
            message = self.client.messages.create(
                body=f"{user_id}|{day}|{prayer}: {msg}\nReply y/n",
                messaging_service_sid=TWILIO_MESSAGING_SID,
                to=phone,
                schedule_type="fixed",
                send_at=send_at
            )
            print(f"Scheduled {prayer} for {send_at}: {message.sid}")