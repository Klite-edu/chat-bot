import sqlite3


# Connect to database
conn = sqlite3.connect("chats.db")
cursor = conn.cursor()

# Create table
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS chats (
#         chat TEXT,
#         user_id INTEGER,
#         role TEXT
#     )
# """)
# conn.commit()

# # Deleting table
# cursor.execute("""
#     DROP TABLE chats
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
# # # Fetch data
# def test(user_id):
#     cursor.execute("SELECT * FROM chats")
#     users = cursor.fetchall()
#     for i in users:
#         if i[2] == 'user' and i[1] == user_id:
#             print(i)

# Update data
# cursor.execute("UPDATE users SET age = ? WHERE name = ?", (26, "Alice"))
# conn.commit()

# Delete data
# cursor.execute("DELETE FROM users WHERE name = ?", ("Alice",))
# conn.commit()

# Close connection
conn.close()
