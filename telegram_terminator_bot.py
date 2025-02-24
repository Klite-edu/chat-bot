from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from remote_ollama import chat_bot

TOKEN: Final = '7615450891:AAFOtX0zvSeAxPEYdxk-mmeYCwIQ8IJhkcQ'
BOT_USERNAME: Final = '@tyler_terminator_bot'

timezone = pytz.timezone('Asia/Kolkata')  # IST timezone (you can replace with pytz.utc for UTC)

scheduler = AsyncIOScheduler(timezone=timezone)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello Thankx for chatting with me I am T-800')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am T-800 psl type something so i can respond')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command')

# Responses
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_text)
        else:
            return 
    else:
        response: str = handle_responses(text)

    print('Bot', response)
    await update.message.reply_text(response)

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error {context.error}')

# Inside the main function
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Add error handler
    app.add_error_handler(error)  # Correct way to add the error handler

    # Start the scheduler before running the bot
    # scheduler.start()

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)
