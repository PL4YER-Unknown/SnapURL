CREATE TABLE IF NOT EXISTS urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(16) NOT NULL UNIQUE,
    long_url TEXT NOT NULL,
    clicks BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_short_code
ON urls (short_code);

CREATE INDEX IF NOT EXISTS idx_clicks
ON urls (clicks);
