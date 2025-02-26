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

# ✅ Thread-safe storage for user messages
user_queues = {}
user_last_message_time = {}

executor = ThreadPoolExecutor(max_workers=50)  # ✅ Adjust based on system capability
queue_lock = threading.Lock()
bot_event_loop = None  # ✅ Stores the event loop
stop_event = threading.Event()  # ✅ Tracks shutdown state


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received /start command from {update.message.chat.id}")
    await update.message.reply_text('Hello! I am your bot. Ask me anything!')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    text = update.message.text
    print(f"Received message from {user_id}: {text}")

    with queue_lock:
        if user_id not in user_queues:
            user_queues[user_id] = queue.Queue()
        user_last_message_time[user_id] = time.time()

        # ✅ Clear previous messages and only keep the latest one
        while not user_queues[user_id].empty():
            user_queues[user_id].get_nowait()  # Remove older messages
        
        user_queues[user_id].put((update, context))  

    # ✅ Start processing in a separate thread
    executor.submit(process_user_messages, user_id)


def process_user_messages(user_id):
    """Processes only the latest message per user after 3 seconds."""
    global bot_event_loop

    while not stop_event.is_set():  
        try:
            user_queue = user_queues.get(user_id)
            if not user_queue or user_queue.empty():
                return  # ✅ Exit if no messages

            # ✅ Wait 3 seconds before processing the latest message
            while True:
                if stop_event.is_set():
                    return  
                time_since_last_message = time.time() - user_last_message_time.get(user_id, 0)
                if time_since_last_message >= 3:
                    break
                time.sleep(0.1)  # ✅ Prevent CPU overuse

            # ✅ Fetch the latest message only
            latest_update, latest_context = user_queue.get_nowait()

            # ✅ Ensure update/context/message is valid
            if not latest_update or not latest_context or not latest_update.message:
                continue  

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

            # ✅ Send response using the event loop
            if bot_event_loop:
                asyncio.run_coroutine_threadsafe(
                    latest_context.bot.send_message(chat_id=latest_update.message.chat_id, text=response),
                    bot_event_loop
                )
                print(f"✅ Reply sent to {user_id}")
            else:
                print(f"❌ ERROR: bot_event_loop is None. Cannot send message.")

        except queue.Empty:
            continue  
        except Exception as e:
            print(f"❌ ERROR in process_user_messages({user_id}): {e}")
            break  


async def stop_bot():
    """Gracefully stops the bot."""
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
