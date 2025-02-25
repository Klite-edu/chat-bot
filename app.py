from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import sqlite3
import pytz
from remote_ollama import chat_bot

TOKEN: Final = '7615450891:AAFOtX0zvSeAxPEYdxk-mmeYCwIQ8IJhkcQ'
BOT_USERNAME: Final = '@tyler_terminator_bot'

# Flask setup
app = Flask(__name__)

# Setting the timezone
timezone = pytz.timezone('Asia/Kolkata')  # IST timezone (you can replace with pytz.utc for UTC)

# Define a function to save chat to the database
def write_in_db(text, user_id, role):
    conn = sqlite3.connect("chats.db")
    cursor = conn.cursor()
    
    # Create table if it doesn't exist (you can do this once outside of the functions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        chat TEXT,
        user_id INTEGER,
        role TEXT
    )
    """)

    cursor.execute("INSERT INTO chats (chat, user_ID, role) VALUES (?, ?, ?)", (text, user_id, role))
    conn.commit()
    conn.close()

# Responses for handling user input
def handle_responses(text, user_id) -> str:
    processed: str = text.lower()
    return chat_bot(text, user_id)

# Define command functions
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello Thanks for chatting with me I am Hal')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am Hal psl type something so I can respond')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command')

# Function to handle incoming messages
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
    print(f'Bot response: {response}')
    await update.message.reply_text(response)

# Error handler function
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error {context.error}')

# Flask Webhook route
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return 'OK'

# Inside the main function
if __name__ == '__main__':
    # Initialize the application
    print('Starting bot...')
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('custom', custom_command))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Add error handler
    application.add_error_handler(error)

    # Set webhook for the Telegram bot
    # Ensure to replace with your public URL where Flask app is hosted
    webhook_url = 'https://your-domain.com/' + TOKEN
    application.bot.set_webhook(url=webhook_url)

    # Start Flask app and use polling to listen to updates
    app.run(port=5000)
