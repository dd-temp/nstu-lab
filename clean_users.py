import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

admin_username = os.getenv("ADMIN_USERNAME")
moderator_username = os.getenv("MODERATOR_USERNAME")

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("""
DELETE FROM users
WHERE username NOT IN (?, ?)
""", (admin_username, moderator_username))

conn.commit()
conn.close()
