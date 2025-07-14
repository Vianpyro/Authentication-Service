CREATE OR REPLACE FUNCTION generate_mfa_backup_codes(
    p_word_count INTEGER DEFAULT 10
)
RETURNS TEXT AS $$
DECLARE
    v_words TEXT[];
    v_word TEXT;
    v_code TEXT := '';
    i INTEGER;
BEGIN
    -- Validate input
    IF p_word_count <= 8 OR p_word_count > 20 THEN
        RAISE EXCEPTION 'Word count must be between 8 and 20';
    END IF;

    -- Get random words from wordlist
    SELECT array_agg(word) INTO v_words
    FROM (
        SELECT word
        FROM wordlist
        ORDER BY RANDOM()
        LIMIT p_word_count
    ) random_words;

    -- Check if the number of words is sufficient
    IF array_length(v_words, 1) < p_word_count THEN
        RAISE EXCEPTION 'Not enough words in wordlist. Required: %, Available: %',
            p_word_count, array_length(v_words, 1);
    END IF;

    -- Join words with spaces
    v_code := array_to_string(v_words, ' ');

    RETURN v_code;
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION generate_mfa_backup_codes TO api;
