CREATE OR REPLACE FUNCTION add_session
    (
        _start TIME
        _end TIME
        _description VARCHAR[]
    )
RETURNS NULL LANGUAGE plpgsql AS $$
    INSERT INTO "Sessions" ("start", "end", "description") VALUES (current_date + _start, current_date + _end, _description);
    -- current_date + interval '12 hour'
    -- current_date + time '12:00:00'
END$$
