CREATE TABLE orders (
    id               BIGSERIAL PRIMARY KEY,
    user_id          BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    delivery_address TEXT NOT NULL,
    payment_method   VARCHAR(50) NOT NULL,
    status           VARCHAR(50) NOT NULL DEFAULT 'NEW',
    total            NUMERIC(10, 2) NOT NULL CHECK (total >= 0),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_user_created ON orders(user_id, created_at DESC);
