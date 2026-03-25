CREATE TABLE vinyls (
    id             BIGSERIAL PRIMARY KEY,
    title          VARCHAR(255) NOT NULL,
    artist_id      BIGINT NOT NULL REFERENCES artists(id) ON DELETE RESTRICT,
    price          NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    description    TEXT,
    cover_url      TEXT,
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vinyls_artist ON vinyls(artist_id);
