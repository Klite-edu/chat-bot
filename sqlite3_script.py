import sqlite3

# Connect to database
conn = sqlite3.connect("chats.db")
cursor = conn.cursor()

# Create table
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS chats (
#         chat TEXT
#     )
# """)
# conn.commit()

# Insert data
# cursor.execute("INSERT INTO chats (chat) VALUES (?)", ("Alice",))
# conn.commit()

# Fetch data
cursor.execute("SELECT * FROM chats")
users = cursor.fetchall()
print("Users in database:", users)

# Update data
# cursor.execute("UPDATE users SET age = ? WHERE name = ?", (26, "Alice"))
# conn.commit()

# Delete data
# cursor.execute("DELETE FROM users WHERE name = ?", ("Alice",))
# conn.commit()

# Close connection
conn.close()
