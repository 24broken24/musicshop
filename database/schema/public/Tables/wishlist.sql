-- Избранное: пользователь может добавить пластинку без покупки (видно на ER-диаграмме).
CREATE TABLE wishlist (
    user_id  BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vinyl_id BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, vinyl_id)
);

CREATE INDEX idx_wishlist_user ON wishlist(user_id);
CREATE INDEX idx_wishlist_vinyl ON wishlist(vinyl_id);
