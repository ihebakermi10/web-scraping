from twilio.rest import Client
import os

account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

phone_number_sid = "15417483110"

new_voice_webhook = "https://example.com/your-new-voice-webhook"

updated_number = client.incoming_phone_numbers(phone_number_sid).update(
    voice_url=new_voice_webhook,
    voice_method="POST"  
)

print(f"Updated voice webhook URL: {updated_number.voice_url}")
