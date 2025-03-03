import sqlite3
import threading
import customtkinter as ctk
from datetime import datetime

DB_FILE = "chats.db"

# Initialize CustomTkinter Theme
ctk.set_appearance_mode("dark")  # Dark Mode
ctk.set_default_color_theme("green")  # WhatsApp Green Theme

class ChatViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chat Viewer")
        self.geometry("750x500")
        self.resizable(False, False)

        # Persistent Database Connection
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Layout: Left - User List | Right - Chat Window
        self.frame_left = ctk.CTkFrame(self, width=200, fg_color="#222831")
        self.frame_left.pack(side="left", fill="y")

        self.frame_right = ctk.CTkFrame(self, width=550, fg_color="#1E1E1E")
        self.frame_right.pack(side="right", fill="both", expand=True)

        # User List Panel
        self.user_label = ctk.CTkLabel(self.frame_left, text="Users", font=("Arial", 14, "bold"), text_color="white")
        self.user_label.pack(pady=10)

        self.user_scroll = ctk.CTkScrollableFrame(self.frame_left, width=180, fg_color="#1E1E1E")
        self.user_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh_button = ctk.CTkButton(self.frame_left, text="Refresh", command=self.refresh_users, fg_color="green")
        self.refresh_button.pack(pady=10)

        # Chat Display Panel
        self.chat_label = ctk.CTkLabel(self.frame_right, text="Chat Messages", font=("Arial", 14, "bold"), text_color="white")
        self.chat_label.pack(pady=10)

        self.chat_scroll = ctk.CTkScrollableFrame(self.frame_right, width=520, fg_color="#1E1E1E")
        self.chat_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.user_buttons = []
        self.refresh_users()

    def fetch_users(self):
        """Fetch unique user IDs from the database."""
        self.cursor.execute("SELECT DISTINCT user_ID FROM chats ORDER BY user_ID ASC")
        return [str(row[0]) for row in self.cursor.fetchall()]

    def fetch_chats(self, user_id):
        """Fetch chat history for the selected user."""
        self.cursor.execute("PRAGMA table_info(chats)")
        columns = [col[1] for col in self.cursor.fetchall()]
        
        if "timestamp" in columns:
            self.cursor.execute("SELECT chat, role, timestamp FROM chats WHERE user_ID = ? ORDER BY ROWID ASC", (user_id,))
        else:
            self.cursor.execute("SELECT chat, role FROM chats WHERE user_ID = ? ORDER BY ROWID ASC", (user_id,))
        
        return self.cursor.fetchall()

    def delete_chats(self, user_id):
        """Delete chat history for a specific user."""
        self.cursor.execute("DELETE FROM chats WHERE user_ID = ?", (user_id,))
        self.conn.commit()

    def refresh_users(self):
        """Refresh the user list (Runs in a separate thread for better performance)."""
        threading.Thread(target=self._refresh_users_thread, daemon=True).start()

    def _refresh_users_thread(self):
        """Threaded function to update user list faster."""
        users = self.fetch_users()

        self.user_scroll.after(0, lambda: self._update_user_list(users))

    def _update_user_list(self, users):
        """Update user list UI efficiently."""
        for widget in self.user_scroll.winfo_children():
            widget.destroy()

        for user in users:
            btn = ctk.CTkButton(self.user_scroll, text=user, command=lambda u=user: self.display_chat(u), fg_color="#008069")
            btn.pack(fill="x", pady=2)

            delete_button = ctk.CTkButton(self.user_scroll, text="Delete Chat", command=lambda u=user: self.confirm_delete(u), fg_color="red")
            delete_button.pack(fill="x", pady=2)

            self.user_buttons.append(btn)

    def confirm_delete(self, user_id):
        """Custom confirmation dialog before deleting the user's chat."""
        # Create a new window for confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Deletion")
        dialog.geometry("300x150")
        dialog.resizable(False, False)

        # Label for dialog
        confirm_label = ctk.CTkLabel(dialog, text=f"Are you sure you want to delete chat history for user {user_id}?", font=("Arial", 12))
        confirm_label.pack(pady=20)

        # Button to confirm deletion
        def on_delete_confirm():
            self.delete_chats(user_id)
            self.refresh_users()  # Refresh the user list to reflect the changes
            self.chat_scroll.after(0, lambda: self._update_chat_ui([]))  # Clear chat window
            dialog.destroy()

        # Button to cancel deletion
        def on_delete_cancel():
            dialog.destroy()

        confirm_button = ctk.CTkButton(dialog, text="Yes", command=on_delete_confirm, fg_color="green")
        confirm_button.pack(side="left", padx=20, pady=10)

        cancel_button = ctk.CTkButton(dialog, text="No", command=on_delete_cancel, fg_color="red")
        cancel_button.pack(side="right", padx=20, pady=10)

    def display_chat(self, user_id):
        """Load chat messages asynchronously for better UI speed."""
        threading.Thread(target=self._load_chat, args=(user_id,), daemon=True).start()

    def _load_chat(self, user_id):
        """Threaded chat loading to avoid UI lag."""
        chats = self.fetch_chats(user_id)

        self.chat_scroll.after(0, lambda: self._update_chat_ui(chats))

    def _update_chat_ui(self, chats):
        """Update chat UI efficiently instead of destroying everything."""
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

        for chat_info in chats:
            if len(chat_info) == 3:
                chat, role, timestamp = chat_info
                formatted_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
            else:
                chat, role = chat_info
                formatted_time = ""

            # Message Style
            if role == "User":
                message_frame = ctk.CTkFrame(self.chat_scroll, fg_color="#075E54", corner_radius=10)
                text_align = "w"
                text_color = "white"
                anchor = "w"
                padx_val = (10, 100)  # User messages left
            else:
                message_frame = ctk.CTkFrame(self.chat_scroll, fg_color="#128C7E", corner_radius=10)
                text_align = "e"
                text_color = "white"
                anchor = "e"
                padx_val = (100, 10)  # Bot messages right

            message_frame.pack(fill="x", anchor=anchor, padx=padx_val, pady=3)

            message_label = ctk.CTkLabel(message_frame, text=chat, font=("Arial", 12), text_color=text_color, wraplength=400, justify="left")
            message_label.pack(padx=10, pady=(5, 0), anchor=text_align)

            if formatted_time:
                time_label = ctk.CTkLabel(message_frame, text=formatted_time, font=("Arial", 8), text_color="lightgray")
                time_label.pack(padx=10, pady=(0, 5), anchor=text_align)

        self.chat_scroll.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1)  # Auto-scroll to latest message

    def on_closing(self):
        """Close database connection on exit."""
        self.conn.close()
        self.destroy()

# Run the UI
if __name__ == "__main__":
    app = ChatViewerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()



# Connect to database
# conn = sqlite3.connect("chats.db")
# cursor = conn.cursor()


# Create table


# # ✅ Create `user_names` table to store user IDs and names
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS user_names (
#         user_id INTEGER PRIMARY KEY,
#         name TEXT
#     )
# """)
# conn.commit()

# Deleting table
# cursor.execute("""
#     DROP TABLE chats
# """)
# conn.commit()
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS chats (
#         chat TEXT,
#         user_id INTEGER,
#         role TEXT
#     )
# """)
# conn.commit()
# cursor.execute("""
#     DROP TABLE user_names
# """)
# conn.commit()


# View table structure / schema
# tables = cursor.fetchall()
# for table in tables:
#     print(table[0])

# Insert data
# cursor.execute("INSERT INTO chats (chat, user_ID, role) VALUES (?, ?, ?)", ("Alice", "Bot", "User/Bot", ))
# conn.commit()

# cursor.execute("SELECT * FROM chats")
# users = cursor.fetchall()
# print(users)
# conn.commit()
# cursor.execute("SELECT * FROM user_names")
# users = cursor.fetchall()
# print(users)
# conn.commit()
# # # Fetch data
# def test(user_id):
# cursor.execute("SELECT * FROM chats")
# users = cursor.fetchall()
# for i in users:
#         if i[2] == 'User' and i[1] == 1103408930:
#                 print(i[0])
# #     if i[2] == 'user' and i[1] == '1103408930':
        
# print(users)

# Update data
# cursor.execute("UPDATE users SET age = ? WHERE name = ?", (26, "Alice"))
# conn.commit()

# Delete data
# cursor.execute("DELETE FROM users WHERE name = ?", ("Alice",))
# conn.commit()

# Close connection
# conn.close()
