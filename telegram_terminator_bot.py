import sqlite3
import asyncio
import threading
import time
import queue
import os
import logging
import openai
import base64
from typing import Final
from telegram import Update
from remote_ollama import chat_bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
# getting keys and tokens


# ✅ Load environment variables from .env
load_dotenv()

# ✅ OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")
ADMIN_USER_ID = 1103408930

# ✅ User message queues
user_queues = {}
user_last_message_time = {}
user_processing_threads = {}
queue_lock = threading.Lock()
bot_event_loop = None
stop_event = threading.Event()
DB_FILE = "chats.db"

# ✅ Create a folder for storing received images
if not os.path.exists("images"):
    os.makedirs("images")


# ✅ Save messages to database
def save_chat(user_id, chat, role):
    """Saves the user and bot chat messages."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (user_ID, chat, role) VALUES (?, ?, ?)", (user_id, chat, role))
    conn.commit()
    conn.close()



# ✅ Handle images sent by users
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    user_name = update.message.chat.first_name
    photo = update.message.photo[-1]  # Get the highest resolution image
    file = await context.bot.get_file(photo.file_id)

    # ✅ Save image to folder
    image_path = f"images/{user_id}_{int(time.time())}.jpg"
    await file.download_to_drive(image_path)

    print(f"✅ Image received from {user_id}: {image_path}")

    # ✅ Process image with GPT-4o
    response, is_valid = analyze_image(image_path, user_id)

    # ✅ Forward image to Admin/Support Team
    if is_valid:
        await context.bot.send_photo(chat_id=ADMIN_USER_ID, photo=file.file_id, caption=(
        f"📸 New image received from {user_id}.\n"
        f"🔍 User Name: {user_name}\n\n"
    ))
        await update.message.reply_text("Thank You For Sharing the Image, Our Experts Will Contact You Shortly")
    # ✅ Send the response to the user
    else:
        await update.message.reply_text("Pls Share a image of Hard Drive,SSD,etc or a clearer image")
    


# ✅ Analyze images using GPT-4o
def analyze_image(image_path, user_id):
    """Processes an image using GPT-4o for verification and analysis."""
    try:
        # ✅ Read image and encode in Base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        # ✅ Ask GPT-4o to describe the image
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            api_key=OPENAI_API_KEY,
            messages=[
                {"role": "system", "content": "Analyze this image and describe its content in a few words."},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]}
            ],
            max_tokens=50  # ✅ Keep response short
        )

        # ✅ Extract description from response
        description = response["choices"][0]["message"]["content"].strip().lower()
        print(f"🔍 Image Description: {description}")

        # ✅ Check if it's a valid hard disk or SSD image
        valid_keywords = ["hard disk", "hdd", "ssd", "storage device", "external drive", "internal drive", "hard drive"]
        if any(keyword in description for keyword in valid_keywords):
            return f"✅ This image appears to be a valid {description}. How can I assist you?", True
        else:
            return "❌ This image does not seem to be a hard disk or SSD. Please send a clear image of your storage device.", False

    except Exception as e:
        logging.error(f"Error analyzing image: {e}")
        return "Sorry, there was an issue analyzing the image."


# ✅ Handle text messages with a 2-second delay
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    text = update.message.text
    print(f"Received message from {user_id}: {text}")

    save_chat(user_id, text, "User")  # ✅ Save user message

    with queue_lock:
        if user_id not in user_queues:
            user_queues[user_id] = queue.Queue()

        user_queues[user_id].put((update, context))
        user_last_message_time[user_id] = time.time()

    # ✅ Start a background thread to process messages with delay
    if user_id not in user_processing_threads:
        user_processing_threads[user_id] = threading.Thread(target=process_user_messages, args=(user_id,))
        user_processing_threads[user_id].start()


# ✅ Process messages after 2 seconds of inactivity
def process_user_messages(user_id):
    """Processes the last message after 2 seconds of inactivity."""
    global bot_event_loop

    while not stop_event.is_set():
        try:
            with queue_lock:
                if user_id not in user_queues or user_queues[user_id].empty():
                    time.sleep(0.1)
                    continue

            # ✅ Wait for 2 seconds before responding
            time_since_last_message = time.time() - user_last_message_time[user_id]
            if time_since_last_message < 2:
                time.sleep(0.1)
                continue

            latest_update, latest_context = None, None
            while not user_queues[user_id].empty():
                latest_update, latest_context = user_queues[user_id].get_nowait()

            if not latest_update or not latest_context or not latest_update.message:
                continue

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

            # ✅ Send the response
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


# ✅ Main function to start the bot
async def main():
    global bot_event_loop, app
    print('Starting bot...')
    
    app = Application.builder().token(TOKEN).build()
    bot_event_loop = asyncio.get_event_loop()

    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # ✅ Handle images

    print('Polling...')
    await app.initialize()
    
    try:
        await app.start()
        await app.updater.start_polling()
        print("Bot is running... Press CTRL+C to stop.")

        while not stop_event.is_set():
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
        stop_event.set()
        print("✅ Bot stopped successfully.")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("Event loop created, starting bot...")
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n🛑 KeyboardInterrupt detected. Stopping bot...")
        stop_event.set()
        print("✅ Bot stopped successfully.")
