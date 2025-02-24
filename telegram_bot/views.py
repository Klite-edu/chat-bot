import json
from django.http import JsonResponse
from telegram import Update
from telegram.ext import Application
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from remote_ollama import chat_bot
from telegram_bot.models import Users

@csrf_exempt  # Disable CSRF for this webhook view
def webhook(request):
    if request.method == 'POST':
        try:
            # Parse the incoming webhook data
            payload = json.loads(request.body)
            update = Update.de_json(payload, None)
            
            # Get user data from the update
            user = update.message.from_user
            user_id = user.id
            user_name = user.first_name

            # Check if the user exists, if not create it
            user_obj, created = Users.objects.get_or_create(user_id=user_id, user_name=user_name)

            # Handle the message
            text = update.message.text
            response = chat_bot(text)

            # Send the response back to the user
            update.message.reply_text(response)
            
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request method"})
