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