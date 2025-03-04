from flask import Flask, request, jsonify
import os
import sqlite3
import openai
from dotenv import load_dotenv
from remote_ollama import chat_bot

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_FILE = "chats.db"

app = Flask(__name__)

# Ensure database exists
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_ID INTEGER,
                        chat TEXT,
                        role TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Save chat messages
def save_chat(user_id, chat, role):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (user_ID, chat, role) VALUES (?, ?, ?)", (user_id, chat, role))
    conn.commit()
    conn.close()

# Get chat history
def get_chat_history(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat FROM chats WHERE user_ID = ?", (user_id,))
    previous_chat = [row[0] for row in cursor.fetchall()]
    conn.close()
    return "\n".join(previous_chat[-20:])  # Last 20 messages


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message")
    
    if not user_id or not message:
        return jsonify({"error": "Missing user_id or message"}), 400
    
    response = chat_bot(message, user_id)
    save_chat(user_id, message, "User")
    save_chat(user_id, response, "Bot")
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)