-- Схема MusicShopDB (согласованная версия 1.0)

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id                BIGSERIAL PRIMARY KEY,
    email             VARCHAR(255) NOT NULL UNIQUE,
    password_hash     TEXT NOT NULL,
    role              VARCHAR(20) NOT NULL DEFAULT 'user'
        CHECK (role IN ('user', 'admin')),
    email_verified_at TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE artists (
    id   BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE genres (
    id   BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE vinyls (
    id            BIGSERIAL PRIMARY KEY,
    title         VARCHAR(255) NOT NULL,
    artist_id     BIGINT NOT NULL REFERENCES artists(id) ON DELETE RESTRICT,
    price         NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    description   TEXT,
    cover_url     TEXT,
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE vinyl_genres (
    vinyl_id BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    genre_id BIGINT NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (vinyl_id, genre_id)
);

CREATE TABLE carts (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE cart_items (
    id         BIGSERIAL PRIMARY KEY,
    cart_id    BIGINT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    vinyl_id   BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (cart_id, vinyl_id)
);

CREATE TABLE orders (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    delivery_address TEXT NOT NULL,
    payment_method   VARCHAR(50) NOT NULL,
    status           VARCHAR(50) NOT NULL DEFAULT 'NEW',
    total            NUMERIC(10, 2) NOT NULL CHECK (total >= 0),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
    id         BIGSERIAL PRIMARY KEY,
    order_id   BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    vinyl_id   BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE RESTRICT,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE reviews (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vinyl_id   BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    rating     SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    body       TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, vinyl_id)
);

CREATE INDEX idx_vinyls_artist ON vinyls(artist_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_reviews_vinyl ON reviews(vinyl_id);