import logging
import sqlite3
import openai
from dotenv import load_dotenv
import os

load_dotenv()
# ✅ OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ✅ Database file
DB_FILE = "chats.db"

# ✅ Instructions for structured replies
instructions = """
You are Alice, a polite and wise assistant for Arun Sharma, a data recovery specialist in Delhi. Your task is to guide users through the data recovery process.

📌 **Conversation Flow**
1️⃣ Greet the user and ask for their name.
➡️ Example: "Hello! I'm Alice, assistant to Arun P Sharma. May I know your name, please?"

2️⃣ Once the user provides their name, ask about their problem.
➡️ Example: "Nice to meet you, [Name]! What issue are you facing with your device?"

3️⃣ After understanding the problem, request an image of the device.
➡️ Example: "Could you please send a photo of your hard disk or SSD? This will help us understand the issue better."

4️⃣ Continue with appropriate responses based on the problem and guide them toward a solution.

📌 **Guidelines**
- Keep responses **concise and polite**.
- If the user doesn’t provide a name, ask again in a friendly manner.
- If the user doesn’t send a photo, gently remind them.
- Ensure responses are clear and in **natural language**.
"""

# ✅ Database functions
def get_db_connection():
    """Returns a thread-safe SQLite connection."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def save_chat(user_id, chat, role):
    """Stores the user’s messages and bot responses in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (user_ID, chat, role) VALUES (?, ?, ?)", (user_id, chat, role))
    conn.commit()
    conn.close()

def get_user_name(user_id):
    """Fetches the stored user name from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat FROM chats WHERE user_ID = ? AND role = 'User'", (user_id,))
    chats = [row[0] for row in cursor.fetchall()]
    conn.close()

    for message in chats:
        words = message.split()
        if len(words) == 1 and words[0].istitle():  # ✅ If single capitalized word
            return words[0]
        if any(kw in message.lower() for kw in ["my name is", "i am", "mera naam", "नाम", "i'm"]):
            return words[-1].capitalize()
    return None

def get_chat_history(user_id):
    """Retrieves the last 20 messages for context."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat FROM chats WHERE user_ID = ? ORDER BY ROWID DESC LIMIT 20", (user_id,))
    previous_chat = [row[0] for row in cursor.fetchall()]
    conn.close()
    return "\n".join(previous_chat) if previous_chat else ""

# ✅ Chat processing function
def chat_bot(message, user_id):
    """Handles the conversation flow and generates responses."""
    chat_history = get_chat_history(user_id)
    user_name = get_user_name(user_id)

    # ✅ Ask for name if unknown
    if not user_name:
        extracted_name = message.split()[-1].capitalize() if len(message.split()) == 1 else None
        if extracted_name:
            save_chat(user_id, extracted_name, "User")  
            return f"Nice to meet you, {extracted_name}! What issue are you facing with your device?"
        else:
            return "Hello! I'm Alice, assistant to Arun P Sharma. May I know your name, please?"

    # ✅ Ask for the problem if not mentioned before
    if "What issue are you facing" not in chat_history:
        return f"Nice to meet you, {user_name}! What issue are you facing with your device?"

    # ✅ Ask for an image if the user hasn’t provided one
    if "Could you please send a photo" not in chat_history:
        return "Could you please send a photo of your hard disk or SSD? This will help us understand the issue better."

    # ✅ Generate responses based on conversation history
    system_prompt = f"Previous chat:\n{chat_history}\n\n{instructions}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            api_key=OPENAI_API_KEY,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.5,
            max_tokens=300,
            top_p=0.9
        )

        # ✅ Extract response content
        gpt_response = response["choices"][0]["message"]["content"].strip()

        # ✅ Save bot response and return
        save_chat(user_id, gpt_response, "Bot")
        return gpt_response

    except Exception as e:
        logging.error(f"Error during API request: {str(e)}")
        return "Sorry, there was an issue. Try again later."
