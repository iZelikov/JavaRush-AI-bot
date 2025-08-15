import os
import sqlite3
import json
from typing import List, Dict, Optional, Any

from aiogram.fsm.storage.base import StorageKey

from storage.abstract_storage import AbstractStorage
from utils.help_load_res import load_sql


class SQLiteStorage(AbstractStorage):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.max_history = os.getenv('MAX_HISTORY')
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()

        # создаём таблицу стейтов (если не существует)
        cursor.execute(load_sql('create_state_table.sql'))

        # Создаем таблицу истории (если не существует)
        cursor.execute(load_sql('create_history_table.sql'))

        # Создаем индекс (отдельным запросом)
        cursor.execute(load_sql('create_index.sql'))

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

    async def get_state(self, key: StorageKey) -> Optional[str]:
        cursor = self.conn.execute(
            "SELECT state FROM fsm_states WHERE user_id = ?",
            (key.user_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    async def set_state(self, key: StorageKey, state: str):
        state_str = state.state if state else None

        with self.conn as conn:
            # Проверяем существование записи
            cursor = conn.execute(
                "SELECT 1 FROM fsm_states WHERE user_id = ?",
                (key.user_id,)
            )
            exists = cursor.fetchone() is not None

            if exists:
                # Обновляем только состояние
                conn.execute(
                    "UPDATE fsm_states SET state = ? WHERE user_id = ?",
                    (state_str, key.user_id)
                )
            else:
                # Создаем новую запись
                conn.execute(
                    "INSERT INTO fsm_states (user_id, state) VALUES (?, ?)",
                    (key.user_id, state_str)
                )

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        with self.conn as conn:
            cursor = conn.execute(
                "SELECT data FROM fsm_states WHERE user_id = ?",
                (key.user_id,)
            )
            row = cursor.fetchone()
            if row and row[0] is not None:  # Проверка на NULL
                return json.loads(row[0])
            return {}

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        with self.conn as conn:
            # Проверяем существование записи
            cursor = conn.execute(
                "SELECT 1 FROM fsm_states WHERE user_id = ?",
                (key.user_id,)
            )
            exists = cursor.fetchone() is not None

            if exists:
                # Обновляем только данные
                conn.execute(
                    "UPDATE fsm_states SET data = ? WHERE user_id = ?",
                    (json.dumps(data), key.user_id)
                )
            else:
                # Создаем новую запись с данными
                conn.execute(
                    "INSERT INTO fsm_states (user_id, data) VALUES (?, ?)",
                    (key.user_id, json.dumps(data))
                )

    async def update_data(self, key: StorageKey, data: Dict[str, Any]):
        current_data = await self.get_data(key)
        current_data.update(data)

        with self.conn as conn:
            conn.execute(
                "UPDATE fsm_states SET data = ? WHERE user_id = ?",
                (json.dumps(current_data), key.user_id)
            )

    async def reset_state(self, key: StorageKey):
        with self.conn as conn:
            conn.execute(
                "DELETE FROM fsm_states WHERE user_id = ?",
                (key.user_id,)
            )

    async def close(self) -> None:
        self.conn.close()