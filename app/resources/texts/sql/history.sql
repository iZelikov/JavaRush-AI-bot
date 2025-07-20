SELECT messages FROM history WHERE user_id = ?

INSERT INTO history (user_id, messages)
VALUES (?, ?) ON CONFLICT(user_id) DO
UPDATE SET messages = excluded.messages

DELETE FROM history WHERE user_id = ?