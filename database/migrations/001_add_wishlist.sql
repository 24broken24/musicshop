-- Модификация БД (ЛР №4): добавление таблицы wishlist к уже существующей MusicShopDB.
-- Выполнить один раз в Query Tool на базе MusicShopDB (или MusicShopDB_Test после развёртывания схемы).

CREATE TABLE wishlist (
    user_id  BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vinyl_id BIGINT NOT NULL REFERENCES vinyls(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, vinyl_id)
);

CREATE INDEX idx_wishlist_user ON wishlist(user_id);
CREATE INDEX idx_wishlist_vinyl ON wishlist(vinyl_id);
