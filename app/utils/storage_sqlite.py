import sqlite3
import json
import os
from typing import List, Dict, Optional
from .storage import HistoryStorage


class SQLiteStorage(HistoryStorage):
    def __init__(self, db_path: str = "chat_history.db"):
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Создаем таблицу при инициализации"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS history
                           (
                               user_id
                               INTEGER
                               PRIMARY
                               KEY,
                               messages
                               TEXT
                               NOT
                               NULL
                               DEFAULT
                               '[]',
                               created_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               updated_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP
                           )
                           ''')

            cursor.execute('''
                           CREATE TRIGGER IF NOT EXISTS update_history_timestamp
                AFTER
                           UPDATE ON history
                               FOR EACH ROW
                           BEGIN
                           UPDATE history
                           SET updated_at = CURRENT_TIMESTAMP
                           WHERE user_id = OLD.user_id;
                           END;
                           ''')
            conn.commit()

    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """Получить историю диалога"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT messages FROM history WHERE user_id = ?",
                (user_id,))
            row = cursor.fetchone()
            return json.loads(row['messages']) if row else []

    async def save_history(self, user_id: int, history: List[Dict[str, str]]):
        """Сохранить историю диалога"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            messages_json = json.dumps(history)

            # Используем UPSERT (INSERT OR REPLACE)
            cursor.execute('''
                           INSERT INTO history (user_id, messages)
                           VALUES (?, ?) ON CONFLICT(user_id) DO
                           UPDATE SET messages = excluded.messages
                           ''', (user_id, messages_json))
            conn.commit()

    async def reset_history(self, user_id: int):
        """Сбросить историю диалога"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM history WHERE user_id = ?",
                (user_id,))
            conn.commit()

    async def cleanup_old_sessions(self, max_age_days: int = 7):
        """Очистка старых сессий"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           DELETE
                           FROM history
                           WHERE julianday('now') - julianday(updated_at) > ?
                           ''', (max_age_days,))
            conn.commit()