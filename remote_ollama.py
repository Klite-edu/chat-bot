from dotenv import load_dotenv
import os
# getting keys and tokens


# ✅ Load environment variables from .env
load_dotenv()

# ✅ OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
import logging
import sqlite3
import openai
from dotenv import load_dotenv
import os

load_dotenv()
# ✅ OpenAI API Key
# ✅ Database file
DB_FILE = "chats.db"

# ✅ Instructions for structured replies
instructions = """**🚀 AI Chatbot Instructions for Manufacturing Business Automation**

### **1. Initial Interaction**
- Greet the user in their **preferred language**.
- Ask for their **business type** (e.g., Automotive, Electronics, Textile, etc.).
- **Skip role question if they are a manufacturer**.
- Ask which **area they need help with**:
  - **CRM** (Leads, customer support, follow-ups)
  - **Sales** (Quotations, orders, inquiries)
  - **Workflow** (Task delegation, production tracking)
  - **Supply Chain** (Inventory, procurement, suppliers)
- Ask **which issue to solve first** and guide accordingly.

---

### **2. CRM Automation**
✅ **Leads**: Log/retrieve leads, store in CRM.
✅ **Support**: Automate tickets & scheduling.
✅ **Follow-ups**: Set reminders, notify teams.

---

### **3. Sales Chatbot**
✅ **Inquiries**: Answer product & stock questions.
✅ **Quotations**: Generate & email PDFs.
✅ **Orders**: Accept, track payments & ERP sync.

---

### **4. Workflow & Task Automation**
✅ **Production**: Assign tasks, track progress.
✅ **Supply Chain**: Automate stock & supplier tracking.
✅ **Employee Tasks**: Auto-assign, notify via chat/SMS.

---

### **5. Reporting & Insights**
✅ **Sales**: Revenue trends, top products.
✅ **Production**: Output, downtime, efficiency.
✅ **Customer**: Chatbot usage, conversions.

---

### **6. Integration with Business Tools**
✅ **Google Workspace (Sheets, Calendar, Chat, Gmail)**
✅ **Salesforce, HubSpot (CRM Integration)**
✅ **ERP Systems (SAP, Odoo, Zoho)**
✅ **WhatsApp API for Customer Communication**

---

### **7. Final Guidance**
✅ **Customize workflows** for specific needs.
✅ **Provide training & guides** for chatbot use.
✅ **Allow escalation** to a human representative.

---

🎯 **Goal:** Automate manufacturing with an AI chatbot for efficiency & growth! 🚀

"""

# ✅ Database functions
def get_db_connection():
    """Returns a thread-safe SQLite connection."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def get_chat_history(user_id):
    """Retrieves the last 20 messages for context."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat FROM chats WHERE user_ID = ?", (user_id,))
    # cursor.execute("SELECT chat FROM chats WHERE user_ID = ? AND role = ? ORDER BY ROWID DESC LIMIT 20", (user_id,'User',))
    previous_chat = [row[0] for row in cursor.fetchall()]
    conn.close()
    # Non repetition filter
    previous_chat_1 = []
    for i in previous_chat:
        if i not in previous_chat_1:
            previous_chat_1.append(i)

    return "\n".join(previous_chat_1)

# ✅ Chat processing function
def chat_bot(message, user_id):
    """Handles the conversation flow and generates responses."""
    chat_history = get_chat_history(user_id)
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
        if message.lower() == 'hi':
            return 'Hi'
        return gpt_response

    except Exception as e:
        logging.error(f"Error during API request: {str(e)}")
        return "Sorry, there was an issue. Try again later."
