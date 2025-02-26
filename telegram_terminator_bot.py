import asyncio
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
from remote_ollama import chat_bot

TOKEN: Final = '7615450891:AAFOtX0zvSeAxPEYdxk-mmeYCwIQ8IJhkcQ'
BOT_USERNAME: Final = '@tyler_terminator_bot'

message_queue = None  

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /start command")
    await update.message.reply_text('Hello, Thanks for chatting with me. I am Hal.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /help command")
    await update.message.reply_text('I am Hal, please type something so I can respond.')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received custom command")
    await update.message.reply_text('This is a custom command.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received message: {update.message.text}")
    await message_queue.put((update, context))

async def process_last_message():
    global message_queue
    while True:
        try:
            print("Waiting 3 seconds before processing the last message...")
            await asyncio.sleep(3)  # ✅ Ensure 3 seconds delay

            if message_queue.empty():
                print("No new messages in queue. Skipping processing.")
                continue  # ✅ If queue is empty, continue waiting

            update, context = None, None
            while not message_queue.empty():
                update, context = await message_queue.get()  # ✅ Get latest message

            text = update.message.text
            user_id = update.message.chat.id
            print(f"Processing latest message: {text} from user {user_id}")

            # 🔴 Step 1: Check if chat_bot() is working
            try:
                response = chat_bot(text, user_id)  # ✅ Call chatbot function
                if not response:
                    response = "I couldn't understand that."
                print(f"Bot Response: {response}")
            except Exception as e:
                print(f"❌ ERROR: chat_bot() failed: {e}")
                response = "Oops, I encountered an error!"

            # 🔴 Step 2: Ensure the bot sends a reply
            try:
                print("Sending reply to user...")
                await update.message.reply_text(response)
                print("✅ Reply sent successfully.")
            except Exception as e:
                print(f"❌ ERROR: Failed to send reply: {e}")

        except Exception as e:
            print(f"❌ ERROR in process_last_message: {e}")


async def main():
    global message_queue
    message_queue = asyncio.Queue()  # ✅ Ensure queue is initialized

    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    asyncio.create_task(process_last_message())  # ✅ Runs message processing in background

    print('Polling...')
    await app.initialize()
    
    try:
        await app.start()
        await app.updater.start_polling()
        print("Bot is running... Press CTRL+C to stop.")

        # ✅ Wait for manual stop (CTRL+C)
        await asyncio.Future()

    except KeyboardInterrupt:
        print("\nBot is stopping... Cleaning up.")
        await app.stop()
        await app.updater.stop()
        print("Bot stopped successfully.")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")



if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("Event loop created, starting bot...")
    loop.run_until_complete(main())
