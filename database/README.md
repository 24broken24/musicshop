# MusicShopDB — SQL-схема (PostgreSQL)

Файлы в `schema/public/Tables/` — по одной таблице на файл (как в примере с Visual Studio).

## Порядок применения (важно из-за внешних ключей)

1. `00_extensions.sql`
2. `users.sql`, `artists.sql`, `genres.sql`
3. `vinyls.sql`
4. `vinyl_genres.sql`
5. `carts.sql`
6. `cart_items.sql`
7. `orders.sql`
8. `order_items.sql`
9. `reviews.sql`

В pgAdmin: Query Tool — выполнить файлы по очереди **или** объединить в один скрипт в этом порядке.

## Полный скрипт одной командой (bash)

```bash
cat schema/public/Tables/00_extensions.sql \
    schema/public/Tables/users.sql \
    schema/public/Tables/artists.sql \
    schema/public/Tables/genres.sql \
    schema/public/Tables/vinyls.sql \
    schema/public/Tables/vinyl_genres.sql \
    schema/public/Tables/carts.sql \
    schema/public/Tables/cart_items.sql \
    schema/public/Tables/orders.sql \
    schema/public/Tables/order_items.sql \
    schema/public/Tables/reviews.sql \
  | psql -h localhost -U postgres -d MusicShopDB
```
