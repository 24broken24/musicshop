CREATE TABLE reviews (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vinyl_id   BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    rating     SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    body       TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, vinyl_id)
);

CREATE INDEX idx_reviews_vinyl ON reviews(vinyl_id);
