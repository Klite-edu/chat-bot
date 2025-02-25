# set_webhook.py

import requests

# Define your bot token
TELEGRAM_API_TOKEN = '7615450891:AAFOtX0zvSeAxPEYdxk-mmeYCwIQ8IJhkcQ'

# The URL of your server where the webhook will be set
WEBHOOK_URL = 'https://1c26-122-162-151-3.ngrok.io/webhook'+ TELEGRAM_API_TOKEN

# Send a request to set the webhook
response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/setWebhook?url={WEBHOOK_URL}')

# Check the response
if response.status_code == 200:
    print("Webhook set successfully!")
else:
    print("Error setting webhook:", response.text)
