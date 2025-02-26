from groq import Groq
import logging
import sqlite3
instructions = """
  👋 Hi! I’m Kartik, your data recovery assistant.
May I know your name? How can I assist? 😊
⏳ I reply within 1-3 minutes.

🔍 Identify the Issue (Max 50 words per message)
Is your hard drive missing, formatted, or clicking?
Has anyone tried fixing it before?
Untouched drive? 📸 Send a photo.
Opened/tampered? ❌ Sorry, we can’t proceed.
💰 Recovery Pricing (Max 50 words per reply)
✔ No Data, No Fee.
✔ Safe & Secure Recovery.

💾 Hard Drive Recovery:

1TB: ₹9,999 - ₹14,999
2TB - 3TB: ₹19,999 - ₹34,999
4TB - 5TB: ₹48,999 - ₹74,999 (Taxes extra)
💾 Clicking Sound (Advanced Recovery):

₹19,999 - ₹1,34,999 (500GB - 5TB)
Donor drive cost may apply.
💾 SSD Recovery: Complex, handled by experts.

🚚 Free pickup for untampered drives!

📜 Important Policy (Max 50 words)
Damaged drives = e-waste (per govt rules).
Under warranty? Return to the brand.
Unclaimed drives (30 days) = e-waste.
📞 Next Steps (Max 50 words)
Need a diagnosis? Let’s begin!

📋 Fill the pickup form:
www.arunp.co/pickup

Would you like to proceed? 😊

Every response follows the 50-word limit while keeping it engaging and human-like. ✅

    """ 


def chat_bot(user_chat, user_id):
    previous_user_chat = []
    conn = sqlite3.connect("chats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats")
    users = cursor.fetchall()
    for i in users:
        if i[2] == 'User' and i[1] == user_id:
            previous_user_chat.append(i[0])
    conn.close()
    chat_history_for_model_2 = []
    for i in previous_user_chat:
        if i not in chat_history_for_model_2:
            chat_history_for_model_2.append(i)
    if len(chat_history_for_model_2 ) <= 20:
        chat_history = "\n".join([i for i in chat_history_for_model_2])
    else:
        chat_history = "\n".join([i for i in chat_history_for_model_2[-20:]])
    # Define the API key
    api_key = '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'
    client = Groq(api_key=api_key)

    global instructions
    instructions_list_1 = instructions[:145] if len(instructions) > 145 else instructions
    # System instructions
    system_instructions = ""

    system_instructions = f"Previous conversation:\n{chat_history}\n"
    system_instructions += '\n' + '\n'.join(instructions_list_1)
    try:
        # Make the API call to get the response from the chat model
        completion = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{"role": "system", "content": system_instructions}, {"role": "user", "content": user_chat}],
            temperature=1,
            max_completion_tokens=512,  # Reduced token length for faster response
            top_p=1,
            stream=False, 
        )

        # Return the response content
        return completion.choices[0].message.content
    
    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"Error during API request: {str(e)}")
        # Return a user-friendly error message
        return "Sorry, there was an issue with the service. Please try again later."
