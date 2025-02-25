from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from remote_ollama import chat_bot
import sqlite3

TOKEN: Final = '7615450891:AAFOtX0zvSeAxPEYdxk-mmeYCwIQ8IJhkcQ'
BOT_USERNAME: Final = '@tyler_terminator_bot'

timezone = pytz.timezone('Asia/Kolkata')  # IST timezone (you can replace with pytz.utc for UTC)

scheduler = AsyncIOScheduler(timezone=timezone)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello Thanks for chatting with me I am Hal')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am Hal psl type something so i can respond')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command')


def write_in_db(text, user_id, role):
    conn = sqlite3.connect("chats.db")
    cursor = conn.cursor()

    # Insert data
    cursor.execute("INSERT INTO chats (chat, user_ID, role) VALUES (?, ?, ?)", (text,user_id,role, ))
    conn.commit()

    conn.close()





# Responses
def handle_responses(text, user_id) -> str:
    processed: str = text.lower()

    return chat_bot(text, user_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    write_in_db(text, update.message.chat.id, 'user')
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_responses(new_text, update.message.chat.id)
        else:
            return 
    else:
        response: str = handle_responses(text, update.message.chat.id)

    write_in_db(response, update.message.chat.id, 'bot')
    print(f'Bot {response}')
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
