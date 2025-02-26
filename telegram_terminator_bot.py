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

# ✅ Thread-safe queues for each user
user_queues = {}
user_last_message_time = {}

executor = ThreadPoolExecutor(max_workers=50)  # ✅ Adjust based on your server
queue_lock = threading.Lock()
bot_event_loop = None  # ✅ Stores the event loop
stop_event = threading.Event()  # ✅ Track shutdown state


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /start command from {update.message.chat.id}")
    await update.message.reply_text('Hello, I am your bot!')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    text = update.message.text
    print(f"Received message from {user_id}: {text}")

    with queue_lock:
        if user_id not in user_queues:
            user_queues[user_id] = queue.Queue()
        user_last_message_time[user_id] = time.time()

    if update and context and update.message:
        user_queues[user_id].put((update, context))  
    else:
        print(f"❌ ERROR: Received invalid update/context for user {user_id}. Skipping.")

    executor.submit(process_user_messages, user_id)


def process_user_messages(user_id):
    """Process messages for a single user in a separate thread."""
    global bot_event_loop

    while not stop_event.is_set():  # ✅ Stop when the event is set
        try:
            user_queue = user_queues.get(user_id)
            if not user_queue or user_queue.empty():
                time.sleep(0.1)
                continue  # ✅ Skip loop if no messages available

            # ✅ Wait until 3 seconds have passed since the last message
            while True:
                if stop_event.is_set():
                    return  # ✅ Exit if stopping
                time_since_last_message = time.time() - user_last_message_time.get(user_id, 0)
                if time_since_last_message >= 3:
                    break
                time.sleep(0.1)

            # ✅ Fetch latest message safely
            latest_update, latest_context = None, None
            while not user_queue.empty():
                item = user_queue.get_nowait()
                if item and isinstance(item, tuple) and len(item) == 2:
                    latest_update, latest_context = item  # ✅ Store latest valid message

            # ✅ Ensure update/context/message is valid
            if not latest_update or not latest_context or not latest_update.message:
                continue  # ✅ Skip and wait for the next message

            text = latest_update.message.text
            print(f"Processing latest message from {user_id}: {text}")

            try:
                response = chat_bot(text, user_id)
                if not response:
                    response = "I couldn't understand that."
                print(f"Bot Response to {user_id}: {response}")
            except Exception as e:
                print(f"❌ ERROR: chat_bot() failed for {user_id}: {e}")
                response = "Oops, I encountered an error!"

            # ✅ Send message using the correct event loop
            if bot_event_loop:
                asyncio.run_coroutine_threadsafe(
                    latest_context.bot.send_message(chat_id=latest_update.message.chat_id, text=response),
                    bot_event_loop
                )
                print(f"✅ Reply sent to {user_id}")
            else:
                print(f"❌ ERROR: bot_event_loop is None. Cannot send message.")

        except queue.Empty:
            continue  # ✅ Ignore empty queue exceptions safely
        except Exception as e:
            print(f"❌ ERROR in process_user_messages({user_id}): {e}")
            break  # Exit thread if there's an error



async def stop_bot():
    """Gracefully stop the bot."""
    print("\n🛑 Received stop signal. Stopping bot...")
    stop_event.set()  # ✅ Stop threads
    executor.shutdown(wait=False)  # ✅ Stop thread pool
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

        # ✅ Keep running until manually stopped
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
