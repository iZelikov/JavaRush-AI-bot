DELETE
FROM history
WHERE julianday('now') - julianday(updated_at) > ?