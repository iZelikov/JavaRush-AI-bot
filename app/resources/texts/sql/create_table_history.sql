CREATE TABLE IF NOT EXISTS history
(
    user_id INTEGER PRIMARY KEY,
    messages TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

CREATE TRIGGER IF NOT EXISTS update_history_timestamp
                AFTER
UPDATE ON history
    FOR EACH ROW
        BEGIN
            UPDATE history
            SET updated_at = CURRENT_TIMESTAMP
            WHERE user_id = OLD.user_id;
        END;