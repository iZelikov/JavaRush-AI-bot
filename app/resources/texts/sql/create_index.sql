CREATE INDEX IF NOT EXISTS idx_chat_history_user_id
    ON chat_history (user_id)