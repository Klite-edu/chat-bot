import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('db.sqlite3')  # Make sure to adjust the path to your SQLite file
cursor = conn.cursor()

# Step 1: Delete all records from Bussiness table
cursor.execute("DELETE FROM model_1_bussiness;")

# Step 2: Delete all records from Client table
cursor.execute("DELETE FROM model_1_client;")

# Step 3: Delete all records from Chats table
cursor.execute("DELETE FROM model_1_chats;")

# Commit the changes
conn.commit()

# Close the connection
conn.close()

print("All records have been deleted from Bussiness, Client, and Chats tables.")
