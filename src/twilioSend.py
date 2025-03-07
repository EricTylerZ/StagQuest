# twilioSend.py
from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN, TWILIO_MESSAGING_SID
from datetime import datetime, timedelta, timezone

class TwilioSender:
    def __init__(self):
        self.client = Client(TWILIO_SID, TWILIO_TOKEN)

    def schedule_day(self, user_id, phone, day, prompts, timezone_offset, start_date):
        """
        Schedule 7 daily prayer texts (Lauds-Compline) for a given day.
        Catholic context: Novena is a 9-day prayer; Saturday and Monday are active,
        Sunday texts are auto-sent by the computer for God-oriented reflection,
        respecting Sabbath rest (Catechism 2184-2188).
        """
        offset = timedelta(hours=timezone_offset)
        now_utc = datetime.now(timezone.utc)  # Modern UTC time
        local_now = now_utc + offset  # Local time (MST)
        day_date = start_date + timedelta(days=day-1)
        prayer_times = {
            "Lauds": 0, "Prime": 1, "Terce": 2, "Sext": 3, "None": 4,
            "Vespers": 5, "Compline": 6
        }
        # Adjust Day 1 to start from now + 5 min if today
        if day == 1 and local_now.date() == day_date:
            base_time = local_now + timedelta(minutes=5)  # Start 5 min from now in MST
            for i, (prayer, _) in enumerate(prayer_times.items()):
                local_send_time = base_time + timedelta(hours=i)  # Space out by hour in MST
                utc_send_time = local_send_time - offset  # Convert to UTC
                send_at = utc_send_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # Format as YYYY-MM-DDTHH:MM:SSZ
                msg = prompts[f"Day {day}"][prayer]
                message = self.client.messages.create(
                    body=f"{user_id}|{day}|{prayer}: {msg}\nReply y/n",
                    messaging_service_sid=TWILIO_MESSAGING_SID,
                    to=phone,
                    schedule_type="fixed",
                    send_at=send_at
                )
                print(f"Scheduled {prayer} for {send_at}: {message.sid}")
        else:
            prayer_times = {
                "Lauds": 6, "Prime": 7, "Terce": 9, "Sext": 12, "None": 15,
                "Vespers": 18, "Compline": 21
            }
            for prayer, hour in prayer_times.items():
                local_send_time = datetime(day_date.year, day_date.month, day_date.day, hour, 0)  # Naive local time
                local_send_time = local_send_time.replace(tzinfo=timezone.utc) + offset  # Make aware, adjust to MST
                utc_send_time = local_send_time - offset  # Convert to UTC
                # Ensure at least 5 min future for subsequent days
                if utc_send_time < now_utc + timedelta(seconds=300):
                    utc_send_time = now_utc + timedelta(seconds=300 + (hour - 6) * 3600)  # Space by hour from now
                send_at = utc_send_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # Format as YYYY-MM-DDTHH:MM:SSZ
                msg = prompts[f"Day {day}"][prayer]
                message = self.client.messages.create(
                    body=f"{user_id}|{day}|{prayer}: {msg}\nReply y/n",
                    messaging_service_sid=TWILIO_MESSAGING_SID,
                    to=phone,
                    schedule_type="fixed",
                    send_at=send_at
                )
                print(f"Scheduled {prayer} for {send_at}: {message.sid}")

    def schedule_initial_days(self, user_id, phone, prompts, timezone_offset):
        """Schedule Days 1-3 (Saturday, Sunday, Monday) starting from today."""
        now_utc = datetime.now(timezone.utc)  # Modern UTC time
        local_now = now_utc + timedelta(hours=timezone_offset)
        start_date = local_now.date()  # Today
        for day in range(1, 4):  # Days 1-3
            self.schedule_day(user_id, phone, day, prompts, timezone_offset, start_date)