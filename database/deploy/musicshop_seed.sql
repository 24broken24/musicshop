-- Seed-данные для демонстрации Sprint 1 (поиск/фильтры/карточки/корзина)
-- Подходит для учебного стенда. Удаляет контент каталога и связей.

BEGIN;

-- очистка каталога
DELETE FROM vinyl_genres;
DELETE FROM vinyls;
DELETE FROM orders;
DELETE FROM order_items;
DELETE FROM cart_items;
DELETE FROM carts;
DELETE FROM wishlist;
DELETE FROM reviews;

DELETE FROM genres;
DELETE FROM artists;

-- артисты
INSERT INTO artists (name) VALUES
  ('Pink Floyd'),
  ('The Beatles'),
  ('Miles Davis');

-- жанры
INSERT INTO genres (name) VALUES
  ('Rock'),
  ('Progressive Rock'),
  ('Jazz');

-- пластинки
INSERT INTO vinyls (title, artist_id, price, description, cover_url, stock_quantity)
SELECT 'The Dark Side of the Moon', a.id, 2900.00, 'Классический альбом Pink Floyd', NULL, 10
FROM artists a WHERE a.name = 'Pink Floyd';

INSERT INTO vinyls (title, artist_id, price, description, cover_url, stock_quantity)
SELECT 'Abbey Road', a.id, 2600.00, 'Легендарный альбом The Beatles', NULL, 8
FROM artists a WHERE a.name = 'The Beatles';

INSERT INTO vinyls (title, artist_id, price, description, cover_url, stock_quantity)
SELECT 'Kind of Blue', a.id, 2300.00, 'Знаковый альбом Miles Davis', NULL, 12
FROM artists a WHERE a.name = 'Miles Davis';

-- связи пластинка-жанр
-- The Dark Side of the Moon: Rock + Progressive Rock
INSERT INTO vinyl_genres (vinyl_id, genre_id)
SELECT v.id, g.id
FROM vinyls v, genres g
WHERE v.title = 'The Dark Side of the Moon'
  AND g.name IN ('Rock', 'Progressive Rock');

-- Abbey Road: Rock
INSERT INTO vinyl_genres (vinyl_id, genre_id)
SELECT v.id, g.id
FROM vinyls v, genres g
WHERE v.title = 'Abbey Road'
  AND g.name IN ('Rock');

-- Kind of Blue: Jazz
INSERT INTO vinyl_genres (vinyl_id, genre_id)
SELECT v.id, g.id
FROM vinyls v, genres g
WHERE v.title = 'Kind of Blue'
  AND g.name IN ('Jazz');

COMMIT;

