import tkinter as tk
from tkinter import scrolledtext
import sqlite3
import openai
import logging
from dotenv import load_dotenv
import os
from remote_ollama import chat_bot

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_FILE = "chats.db"

# ✅ Database functions
def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def get_chat_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat FROM chats WHERE user_ID = ?", (user_id,))
    previous_chat = [row[0] for row in cursor.fetchall()]
    conn.close()
    return "\n".join(set(previous_chat[-20:]))  # Last 20 unique messages

# Saving the user's chats
def save_chat(user_id, chat, role):
    """Saves the user and bot chat messages."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (user_ID, chat, role) VALUES (?, ?, ?)", (user_id, chat, role))
    conn.commit()
    conn.close()

# ✅ GUI Setup
def send_message(event=None):  # Allow Enter key to trigger this function
    user_id = 12345  # Static user ID for simplicity
    message = message_entry.get()
    if not message:
        return
    
    response = chat_bot(message, user_id)
    save_chat(user_id, message, 'User')
    save_chat(user_id, response, 'Bot')
    chat_display.insert(tk.END, f"You: {message}\n", "user")
    chat_display.insert(tk.END, f"Bot: {response}\n", "bot")
    message_entry.delete(0, tk.END)

# ✅ GUI Window (Dark Theme)
root = tk.Tk()
root.title("Chat with Remote Ollama")
root.configure(bg="#1e1e1e")  # Dark background

chat_display = scrolledtext.ScrolledText(root, width=50, height=15, wrap=tk.WORD, bg="#252526", fg="white", insertbackground="white", font=("Arial", 12))
chat_display.grid(row=0, column=0, columnspan=2)
chat_display.tag_config("user", foreground="#569CD6")  # Blue for user
chat_display.tag_config("bot", foreground="#CE9178")  # Orange for bot

message_entry = tk.Entry(root, width=40, bg="#333333", fg="white", insertbackground="white", font=("Arial", 12))
message_entry.grid(row=1, column=0)
message_entry.bind("<Return>", send_message)  # Bind Enter key

send_button = tk.Button(root, text="Send", command=send_message, bg="#007ACC", fg="white", font=("Arial", 12), relief=tk.FLAT)
send_button.grid(row=1, column=1)

root.mainloop()
