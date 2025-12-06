# database.py - Centralized & Finalized Database Management

import sqlite3
import time
import secrets
from config import DEFAULT_UPI_HANDLE, DEFAULT_QR_CODE_URL, DEFAULT_PAYMENT_LINK, DEFAULT_AUTO_DELETE_MINUTES

class Database:
    def __init__(self, db_file="bot.db"):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Creates all necessary tables in the fresh database."""
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_banned INTEGER DEFAULT 0, is_member INTEGER DEFAULT 0
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, message_id INTEGER,
            file_name TEXT, file_type TEXT, file_size INTEGER, uploaded_by INTEGER
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT, batch_name TEXT, start_msg INTEGER, end_msg INTEGER, created_by INTEGER
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS bot_settings (
            setting_key TEXT PRIMARY KEY, setting_value TEXT
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS force_sub_channels (
            channel_id INTEGER PRIMARY KEY, channel_name TEXT
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS user_access (
            user_id INTEGER PRIMARY KEY, unlocked_until TIMESTAMP
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS unlock_tokens (
            token TEXT PRIMARY KEY, user_id INTEGER, original_payload TEXT, expiry TIMESTAMP
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS batch_messages (
            batch_id INTEGER, message_id INTEGER, user_id INTEGER, PRIMARY KEY (batch_id, message_id, user_id)
        )""")
        
        self.cursor.execute("INSERT OR IGNORE INTO bot_settings (setting_key, setting_value) VALUES (?, ?)", ("upi_handle", DEFAULT_UPI_HANDLE))
        self.cursor.execute("INSERT OR IGNORE INTO bot_settings (setting_key, setting_value) VALUES (?, ?)", ("qr_code_url", DEFAULT_QR_CODE_URL))
        self.cursor.execute("INSERT OR IGNORE INTO bot_settings (setting_key, setting_value) VALUES (?, ?)", ("payment_link", DEFAULT_PAYMENT_LINK))
        self.cursor.execute("INSERT OR IGNORE INTO bot_settings (setting_key, setting_value) VALUES (?, ?)", ("auto_delete_minutes", str(DEFAULT_AUTO_DELETE_MINUTES)))
        self.conn.commit()

    def _ensure_user_exists(self, user_id):
        """Private helper to make sure a user record exists before updating."""
        self.cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

    def add_user(self, user):
        self._ensure_user_exists(user.id)
        self.cursor.execute("UPDATE users SET first_name = ?, username = ? WHERE user_id = ?", (user.first_name, user.username, user.id))
        self.conn.commit()

    def get_user_status(self, user_id):
        self.cursor.execute("SELECT is_banned, is_member FROM users WHERE user_id = ?", (user_id,))
        if (res := self.cursor.fetchone()):
            if res[0] == 1: return "banned"
            if res[1] == 1: return "member"
        self.cursor.execute("SELECT unlocked_until FROM user_access WHERE user_id = ? AND unlocked_until > ?", (user_id, time.time()))
        return "unlocked" if self.cursor.fetchone() else "free"

    def set_user_member(self, user_id, is_member: bool):
        self._ensure_user_exists(user_id)
        self.cursor.execute("UPDATE users SET is_member = ? WHERE user_id = ?", (1 if is_member else 0, user_id))
        self.conn.commit()

    def set_user_banned(self, user_id, is_banned: bool):
        self._ensure_user_exists(user_id)
        self.cursor.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (1 if is_banned else 0, user_id))
        self.conn.commit()

    def add_file(self, original_message, sent_msg, file_info):
        self.cursor.execute("INSERT INTO files (chat_id, message_id, file_name, file_type, file_size, uploaded_by) VALUES (?, ?, ?, ?, ?, ?)",
                       (sent_msg.chat.id, sent_msg.id, file_info['name'], file_info['type'], file_info['size'], original_message.from_user.id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_file(self, file_id):
        self.cursor.execute("SELECT chat_id, message_id, file_name FROM files WHERE id=?", (file_id,))
        return self.cursor.fetchone()

    def add_batch(self, name, start_msg, end_msg, admin_id):
        self.cursor.execute("INSERT INTO batches (batch_name, start_msg, end_msg, created_by) VALUES (?, ?, ?, ?)", (name, start_msg, end_msg, admin_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_batch(self, batch_id):
        self.cursor.execute("SELECT batch_name, start_msg, end_msg FROM batches WHERE id=?", (batch_id,))
        return self.cursor.fetchone()

    def add_batch_message(self, batch_id, message_id, user_id):
        """Track message IDs from batch sends for auto-deletion"""
        self.cursor.execute("INSERT OR IGNORE INTO batch_messages (batch_id, message_id, user_id) VALUES (?, ?, ?)", (batch_id, message_id, user_id))
        self.conn.commit()

    def get_batch_messages(self, batch_id, user_id):
        """Get all message IDs from a batch send"""
        self.cursor.execute("SELECT message_id FROM batch_messages WHERE batch_id = ? AND user_id = ?", (batch_id, user_id))
        return [row[0] for row in self.cursor.fetchall()]

    def clear_batch_messages(self, batch_id, user_id):
        """Clear batch message tracking after deletion"""
        self.cursor.execute("DELETE FROM batch_messages WHERE batch_id = ? AND user_id = ?", (batch_id, user_id))
        self.conn.commit()

    def get_setting(self, key):
        self.cursor.execute("SELECT setting_value FROM bot_settings WHERE setting_key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO bot_settings (setting_key, setting_value) VALUES (?, ?)", (key, value))
        self.conn.commit()
    
    def create_unlock_token(self, user_id, payload):
        token = secrets.token_urlsafe(10)
        expiry = time.time() + 900
        self.cursor.execute("INSERT INTO unlock_tokens (token, user_id, original_payload, expiry) VALUES (?, ?, ?, ?)", (token, user_id, payload, expiry))
        self.conn.commit()
        return token
        
    def verify_unlock_token(self, token, user_id):
        self.cursor.execute("SELECT original_payload FROM unlock_tokens WHERE token = ? AND user_id = ? AND expiry > ?", (token, user_id, time.time()))
        if (result := self.cursor.fetchone()):
            self.cursor.execute("DELETE FROM unlock_tokens WHERE token = ?", (token,))
            self.conn.commit()
            return result[0]
        return None
        
    def grant_temporary_access(self, user_id, hours=1):
        unlock_expiry = time.time() + (hours * 3600)
        self.cursor.execute("INSERT OR REPLACE INTO user_access (user_id, unlocked_until) VALUES (?, ?)", (user_id, unlock_expiry))
        self.conn.commit()

    def add_fsub_channel(self, channel_id, channel_name):
        self.cursor.execute("INSERT OR IGNORE INTO force_sub_channels (channel_id, channel_name) VALUES (?, ?)", (channel_id, channel_name))
        self.conn.commit()

    def get_fsub_channels(self):
        return [row[0] for row in self.cursor.execute("SELECT channel_id FROM force_sub_channels").fetchall()]

    def get_stats(self):
        return {
            'files': self.cursor.execute("SELECT COUNT(*) FROM files").fetchone()[0] or 0,
            'users': self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0] or 0,
            'banned': self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1").fetchone()[0] or 0,
            'members': self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_member = 1").fetchone()[0] or 0
        }

    def get_broadcast_users(self):
        return self.cursor.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
