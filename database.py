import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/dating.db")


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gender TEXT,
        looking_for TEXT,
        description TEXT,
        photo_file_id TEXT,
        is_active INTEGER DEFAULT 0,
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER,
        user2_id INTEGER,
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER,
        user2_id INTEGER,
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user_id INTEGER,
        to_user_id INTEGER,
        created_at TEXT
    )''')
    
    conn.commit()
    conn.close()


def add_user(user_id, name, age, gender, looking_for, description, photo_file_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users 
        (user_id, name, age, gender, looking_for, description, photo_file_id, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?) ''',
        (user_id, name, age, gender, looking_for, description, photo_file_id, datetime.now()))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user


def update_user(user_id, name=None, age=None, gender=None, looking_for=None, description=None, photo_file_id=None):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    fields = []
    values = []
    
    if name:
        fields.append('name = ?')
        values.append(name)
    if age:
        fields.append('age = ?')
        values.append(age)
    if gender:
        fields.append('gender = ?')
        values.append(gender)
    if looking_for:
        fields.append('looking_for = ?')
        values.append(looking_for)
    if description:
        fields.append('description = ?')
        values.append(description)
    if photo_file_id:
        fields.append('photo_file_id = ?')
        values.append(photo_file_id)
    
    values.append(user_id)
    
    c.execute(f'UPDATE users SET {", ".join(fields)} WHERE user_id = ?', values)
    conn.commit()
    conn.close()


def deactivate_user(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET is_active = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


def get_active_profiles(user_id, gender_filter):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    if gender_filter == 'both':
        c.execute('SELECT user_id FROM users WHERE user_id != ? AND is_active = 1', (user_id,))
    else:
        c.execute('SELECT user_id FROM users WHERE user_id != ? AND gender = ? AND is_active = 1', (user_id, gender_filter))
    
    profiles = c.fetchall()
    conn.close()
    return [p[0] for p in profiles]


def add_like(from_user_id, to_user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO likes (from_user_id, to_user_id, created_at) VALUES (?, ?, ?)',
        (from_user_id, to_user_id, datetime.now()))
    conn.commit()
    conn.close()


def check_mutual_like(user1_id, user2_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM likes WHERE from_user_id = ? AND to_user_id = ?', (user2_id, user1_id))
    mutual = c.fetchone()
    conn.close()
    return mutual is not None


def create_chat(user1_id, user2_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO chats (user1_id, user2_id, created_at) VALUES (?, ?, ?)',
        (user1_id, user2_id, datetime.now()))
    conn.commit()
    chat_id = c.lastrowid
    conn.close()
    return chat_id


def get_chat(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM chats WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
    chat = c.fetchone()
    conn.close()
    return chat


def get_chat_partner(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM chats WHERE user1_id = ? OR user2_id = ?', (user_id, user_id))
    chat = c.fetchone()
    conn.close()
    
    if not chat:
        return None
    
    if chat[1] == user_id:
        return chat[2]
    else:
        return chat[1]