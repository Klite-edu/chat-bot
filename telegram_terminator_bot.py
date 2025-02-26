import sqlite3
import asyncio
import threading
import time
import queue
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from remote_ollama import chat_bot
from concurrent.futures import ThreadPoolExecutor

TOKEN: Final = '7615450891:AAFOtX0zvSeAxPEYdxk-mmeYCwIQ8IJhkcQ'
BOT_USERNAME: Final = '@tyler_terminator_bot'

# ✅ User message queues
user_queues = {}
user_last_message_time = {}
user_processing_threads = {}

executor = ThreadPoolExecutor(max_workers=50)
queue_lock = threading.Lock()
bot_event_loop = None
stop_event = threading.Event()

DB_FILE = "chats.db"  # ✅ Database file


# ✅ Save messages to database
def save_chat(user_id, chat, role):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (user_ID, chat, role) VALUES (?, ?, ?)", (user_id, chat, role))
    conn.commit()
    conn.close()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /start command from {update.message.chat.id}")
    await update.message.reply_text('Hello! I am your bot. Ask me anything!')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user messages and queues them for processing after inactivity."""
    user_id = update.message.chat.id
    text = update.message.text
    print(f"Received message from {user_id}: {text}")

    save_chat(user_id, text, "User")  # ✅ Save user message

    with queue_lock:
        if user_id not in user_queues:
            user_queues[user_id] = queue.Queue()

        user_queues[user_id].put((update, context))
        user_last_message_time[user_id] = time.time()  # ✅ Update last message time

    # ✅ Start a thread to monitor inactivity and process messages
    if user_id not in user_processing_threads:
        user_processing_threads[user_id] = threading.Thread(target=process_user_messages, args=(user_id,))
        user_processing_threads[user_id].start()


def process_user_messages(user_id):
    """Processes the last message after 2 seconds of inactivity."""
    global bot_event_loop

    while not stop_event.is_set():
        try:
            with queue_lock:
                if user_id not in user_queues or user_queues[user_id].empty():
                    time.sleep(0.1)
                    continue

            time_since_last_message = time.time() - user_last_message_time[user_id]

            if time_since_last_message < 1:
                time.sleep(0.1)
                continue  # ✅ Wait until user stops sending messages for 2 seconds

            # ✅ Get the last message in the queue
            latest_update, latest_context = None, None
            while not user_queues[user_id].empty():
                latest_update, latest_context = user_queues[user_id].get_nowait()

            if not latest_update or not latest_context or not latest_update.message:
                continue  # ✅ Ignore invalid updates

            text = latest_update.message.text
            print(f"Processing latest message from {user_id}: {text}")

            try:
                response = chat_bot(text, user_id)  
                if not response:
                    response = "I couldn't understand that."
                print(f"Bot Response to {user_id}: {response}")

                save_chat(user_id, response, "Bot")  # ✅ Save bot response

            except Exception as e:
                print(f"❌ ERROR: chat_bot() failed for {user_id}: {e}")
                response = "Oops, I encountered an error!"

            if bot_event_loop:
                asyncio.run_coroutine_threadsafe(
                    latest_context.bot.send_message(chat_id=latest_update.message.chat.id, text=response),
                    bot_event_loop
                )
                print(f"✅ Reply sent to {user_id}")
            else:
                print(f"❌ ERROR: bot_event_loop is None. Cannot send message.")

            # ✅ Remove user from processing list
            with queue_lock:
                if user_id in user_processing_threads:
                    del user_processing_threads[user_id]

        except Exception as e:
            print(f"❌ ERROR in process_user_messages({user_id}): {e}")
            break  


async def stop_bot():
    """Gracefully stop the bot."""
    print("\n🛑 Received stop signal. Stopping bot...")
    stop_event.set()  
    executor.shutdown(wait=False)  
    print("🛑 Cleaning up and stopping the bot...")
    await app.stop()
    await app.updater.stop()
    print("✅ Bot stopped successfully.")


async def main():
    global bot_event_loop, app

    print('Starting bot...')
    
    app = Application.builder().token(TOKEN).build()
    bot_event_loop = asyncio.get_event_loop()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print('Polling...')
    await app.initialize()

    try:
        await app.start()
        await app.updater.start_polling()
        print("Bot is running... Press CTRL+C to stop.")

        while not stop_event.is_set():
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        await stop_bot()
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("Event loop created, starting bot...")
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n🛑 KeyboardInterrupt detected. Stopping bot...")
        stop_event.set()
        executor.shutdown(wait=False)
        print("✅ Bot stopped successfully.")
