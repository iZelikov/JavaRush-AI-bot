import os
import sqlite3
import json
from typing import List, Dict, Optional, Any
from storage.abstract_storage import AbstractStorage


class SQLiteStorage(AbstractStorage):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.max_history = os.getenv('MAX_HISTORY')
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()

        # создаём таблицу стейтов (если не существует)
        cursor.execute('''
                          CREATE TABLE IF NOT EXISTS fsm_states
                          (
                              user_id
                              INTEGER
                              PRIMARY
                              KEY,
                              state
                              TEXT,
                              data
                              TEXT
                          )
                          ''')

        # Создаем таблицу истории (если не существует)
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS chat_history
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           role
                           TEXT
                           NOT
                           NULL,
                           content
                           TEXT
                           NOT
                           NULL,
                           timestamp
                           DATETIME
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Создаем индекс (отдельным запросом)
        cursor.execute('''
                       CREATE INDEX IF NOT EXISTS idx_chat_history_user_id
                           ON chat_history(user_id)
                       ''')

        self.conn.commit()

    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE user_id = ?",
            (user_id,)
        )
        return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

    async def save_history(self, user_id: int, history: List[Dict[str, str]]):
        cursor = self.conn.cursor()

        # Удаляем старую историю
        cursor.execute(
            "DELETE FROM chat_history WHERE user_id = ?",
            (user_id,)
        )

        # Вставляем новую историю
        for message in history:
            cursor.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, message["role"], message["content"])
            )

        self.conn.commit()

    async def reset_history(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM chat_history WHERE user_id = ?",
            (user_id,)
        )
        self.conn.commit()

    async def get_state(self, user_id: int) -> Optional[str]:
        cursor = self.conn.execute(
            "SELECT state FROM fsm_states WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    async def set_state(self, user_id: int, state: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_states (user_id, state) VALUES (?, ?)",
                (user_id, state)
            )

    async def get_data(self, user_id: int) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM user_states WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return json.loads(row[0]) if row and row[0] else {}

    async def update_data(self, user_id: int, data: Dict[str, Any]):
        current_data = await self.get_data(user_id)
        current_data.update(data)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE user_states SET data = ? WHERE user_id = ?",
                (json.dumps(current_data), user_id)
            )

    async def reset_state(self, user_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM user_states WHERE user_id = ?",
                (user_id,)
            )