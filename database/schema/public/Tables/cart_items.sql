CREATE TABLE cart_items (
    id       BIGSERIAL PRIMARY KEY,
    cart_id  BIGINT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    vinyl_id BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (cart_id, vinyl_id)
);
