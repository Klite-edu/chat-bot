# telegram_bot/bot.py
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from remote_ollama import chat_bot
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot

def set_webhook():
    bot = Bot(token=TOKEN)
    webhook_url = 'http://127.0.0.1:8000/telegram/webhook/'  # Use your actual domain or ngrok URL
    bot.set_webhook(url=webhook_url)


TOKEN: Final = '7615450891:AAFOtX0zvSeAxPEYdxk-mmeYCwIQ8IJhkcQ'
BOT_USERNAME: Final = '@tyler_terminator_bot'

timezone = pytz.timezone('Asia/Kolkata')  # IST timezone

# Initialize the scheduler
scheduler = AsyncIOScheduler(timezone=timezone)

# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello Thankx for chatting with me I am T-800')

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am T-800 psl type something so i can respond')

# Custom command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command')

# Response handler
def handle_responses(text: str) -> str:
    processed: str = text.lower()
    return chat_bot(text)

    if 'hello' in text:
        return 'Hey, There'
    
    if 'how are you' in text:
        return 'I am good!'

    if 'I love python' in text:
        return 'Remember to subscribe'

    return 'I do not understand what you wrote...'

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response: str = handle_responses(text)

    await update.message.reply_text(response)

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error {context.error}')

# Function to start the bot
def start_bot():
    print('Starting bot...')
    set_webhook()
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Handle text messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Add error handler
    app.add_error_handler(error)

    # Poll the bot (can be swapped for webhook later)
    print('Polling...')
    app.run_polling(poll_interval=3)
