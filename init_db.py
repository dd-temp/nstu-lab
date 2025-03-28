import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")
moderator_username = os.getenv("MODERATOR_USERNAME")
moderator_password = os.getenv("MODERATOR_PASSWORD")

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'moderator', 'user')) NOT NULL
)
''')

cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
               (admin_username, admin_password, "admin"))
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
               (moderator_username, moderator_password, "moderator"))

conn.commit()
conn.close()