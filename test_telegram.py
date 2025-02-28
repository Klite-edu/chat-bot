import sqlite3
import asyncio
import random
import time
import threading
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from remote_ollama import chat_bot  # ✅ Import your bot function

executor = ThreadPoolExecutor(max_workers=30)  # ✅ Reduce workers for stability
stop_event = threading.Event()  # ✅ Allows graceful stopping

# ✅ Simulate multiple users with random messages
users = [f"user_{i}" for i in range(1000)]  # ✅ 500 test users
messages = ["Hello!", "Need help?", "Tell me about SSD recovery", "My hard disk is not working", "What's the cost?"]

# ✅ API Key & Model Rotation
api_keys = [
    "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",
    "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",
    "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",
    "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"
]  
model_list = [
    'llama-3.1-8b-instant', 'qwen-2.5-32b', 'gemma2-9b-it',
    'deepseek-r1-distill-qwen-32b', 'llama3-8b-8192'
]

latency_records = []  # ✅ Store Groq API latencies
response_time_records = []  # ✅ Store total response times
rate_limit_reached = threading.Event()  # ✅ Stop test if rate limit is hit

def get_random_api_key():
    """Get a random API key to avoid rate limits."""
    return random.choice(api_keys)

def get_random_model():
    """Get a random model, preferring smaller ones first."""
    return random.choice(model_list)

def get_db_connection():
    """Create a new SQLite connection (thread-safe)."""
    return sqlite3.connect("chats.db", check_same_thread=False)

def save_chat(user_id, chat, role):
    """Save chat to SQLite database (with retry logic)."""
    attempt = 0
    while attempt < 3:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chats (user_ID, chat, role) VALUES (?, ?, ?)", (user_id, chat, role))
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                wait_time = random.uniform(0.2, 0.5)  # ✅ Short wait before retrying
                print(f"⚠️ Database locked! Retrying in {wait_time:.2f}s...", flush=True)
                time.sleep(wait_time)
                attempt += 1
            else:
                print(f"❌ SQLite Error: {e}", flush=True)
                break  # ✅ Stop retrying on non-lock errors

def test_bot(user_id):
    """Simulate a user sending messages to the bot and measure latency & response time."""
    while not stop_event.is_set() and not rate_limit_reached.is_set():
        time.sleep(random.uniform(0.1, 2))  # ✅ Simulate random typing delay

        if stop_event.is_set() or rate_limit_reached.is_set():
            break  # ✅ Stop immediately if test is ending

        message = random.choice(messages)
        api_key = get_random_api_key()  # ✅ Get a random API key
        model = get_random_model()  # ✅ Get a random model

        response_start_time = time.time()  # ✅ Start total response time timer

        print(f"\n📨 {user_id} sent: {message} (API Key: {api_key[-6:]}, Model: {model})", flush=True)

        attempt = 0
        while attempt < 3:  # ✅ Retry up to 3 times
            try:
                api_start_time = time.time()  # ✅ Start Groq API latency timer
                response = chat_bot(message, user_id, api_key, model)  # ✅ Call chat bot
                api_end_time = time.time()  # ✅ Stop Groq API latency timer

                latency = api_end_time - api_start_time  # ✅ Calculate Groq API latency
                latency_records.append(latency)

                response_end_time = time.time()  # ✅ Stop total response time timer
                response_time = response_end_time - response_start_time  # ✅ Calculate total response time
                response_time_records.append(response_time)

                # ✅ Save user & bot chat in database
                save_chat(user_id, message, "User")
                save_chat(user_id, response, "Bot")

                # ✅ Print response with both latency metrics
                print(f"\n🤖 {user_id} received: {response} (Latency: {latency:.3f}s, Response Time: {response_time:.3f}s)", flush=True)
                sys.stdout.flush()  # ✅ Force print update
                break  # ✅ Exit retry loop after success

            except Exception as e:
                if "rate_limit_exceeded" in str(e):
                    rate_limit_reached.set()  # ✅ Stop all threads if rate limit is hit
                    print(f"\n⛔ Rate limit hit! Stopping all tests now.", flush=True)
                    return  # ✅ Exit this function immediately
                else:
                    print(f"\n❌ {user_id} ERROR: {e}", flush=True)
                    time.sleep(2)  # ✅ Short wait before retrying
                    attempt += 1  # ✅ Retry next attempt

async def run_tests():
    """Continuously send messages from multiple users in parallel."""
    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(executor, test_bot, user) for user in users]
    await asyncio.gather(*tasks, return_exceptions=True)

# ✅ Run the test
try:
    asyncio.run(run_tests())  # ✅ Runs until CTRL + C or rate limit is hit
except KeyboardInterrupt:
    print("\n🛑 Stopping test...", flush=True)
    stop_event.set()  # ✅ Tell threads to stop immediately
    executor.shutdown(wait=False)  # ✅ Stop threads

    # ✅ Calculate average latency and response time
    if latency_records and response_time_records:
        avg_latency = sum(latency_records) / len(latency_records)
        avg_response_time = sum(response_time_records) / len(response_time_records)
        print(f"\n📊 Average Groq API Latency: {avg_latency:.3f}s", flush=True)
        print(f"📊 Average Response Time: {avg_response_time:.3f}s", flush=True)
    else:
        print("\n⚠ No latency or response time data recorded.", flush=True)

    print("✅ Test stopped successfully.", flush=True)
