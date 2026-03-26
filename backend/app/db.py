import os
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras


def _normalize_database_url(database_url: str) -> str:
    """
    In .env we may use SQLAlchemy-style scheme `postgresql+psycopg2://...`.
    psycopg2 expects `postgresql://...`.
    """
    return database_url.replace("postgresql+psycopg2://", "postgresql://")


def get_conn():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in environment (.env).")
    dsn = _normalize_database_url(database_url)
    return psycopg2.connect(dsn)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, email, password_hash, role FROM users WHERE email = %s",
                (email,),
            )
            return cur.fetchone()


def create_user(email: str, password_hash: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, password_hash, role, email_verified_at)
                VALUES (%s, %s, 'user', NOW())
                RETURNING id
                """,
                (email, password_hash),
            )
            user_id = cur.fetchone()[0]
            return user_id


def ensure_cart(user_id: int) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM carts WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(
                "INSERT INTO carts (user_id) VALUES (%s) RETURNING id",
                (user_id,),
            )
            return cur.fetchone()[0]


def add_to_cart(user_id: int, vinyl_id: int, quantity: int = 1) -> None:
    if quantity <= 0:
        return
    cart_id = ensure_cart(user_id)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cart_items (cart_id, vinyl_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (cart_id, vinyl_id)
                DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity
                """,
                (cart_id, vinyl_id, quantity),
            )


def get_cart_count(user_id: int) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(SUM(ci.quantity), 0)
                FROM cart_items ci
                JOIN carts c ON c.id = ci.cart_id
                WHERE c.user_id = %s
                """,
                (user_id,),
            )
            return int(cur.fetchone()[0])


def get_cart_items(user_id: int) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    v.id AS vinyl_id,
                    v.title,
                    v.price,
                    ci.quantity,
                    (v.price * ci.quantity) AS line_total
                FROM cart_items ci
                JOIN carts c ON c.id = ci.cart_id
                JOIN vinyls v ON v.id = ci.vinyl_id
                WHERE c.user_id = %s
                ORDER BY v.id
                """,
                (user_id,),
            )
            return list(cur.fetchall())

def clear_cart(user_id: int) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM cart_items
                WHERE cart_id IN (SELECT id FROM carts WHERE user_id = %s)
                """,
                (user_id,),
            )


def create_order_from_cart(user_id: int, delivery_address: str, payment_method: str) -> int:
    """
    Creates an order from current cart items and clears the cart.
    Returns created order_id.
    """
    items = get_cart_items(user_id)
    total = sum(float(i["line_total"]) for i in items) if items else 0.0
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (user_id, delivery_address, payment_method, status, total)
                VALUES (%s, %s, %s, 'NEW', %s)
                RETURNING id
                """,
                (user_id, delivery_address, payment_method, total),
            )
            order_id = cur.fetchone()[0]
            for i in items:
                cur.execute(
                    """
                    INSERT INTO order_items (order_id, vinyl_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, i["vinyl_id"], i["quantity"], i["price"]),
                )
            cur.execute(
                "DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE user_id = %s)",
                (user_id,),
            )
            return order_id


def _get_or_create_artist_id(cur, name: str) -> int:
    cur.execute("SELECT id FROM artists WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO artists (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]


def _get_or_create_genre_id(cur, name: str) -> int:
    cur.execute("SELECT id FROM genres WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO genres (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]


def create_vinyl(
    title: str,
    artist_name: str,
    genre_names: List[str],
    price: float,
    description: Optional[str],
) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            artist_id = _get_or_create_artist_id(cur, artist_name)
            cur.execute(
                """
                INSERT INTO vinyls (title, artist_id, price, description, stock_quantity)
                VALUES (%s, %s, %s, %s, 0)
                RETURNING id
                """,
                (title, artist_id, price, description),
            )
            vinyl_id = cur.fetchone()[0]
            for g in genre_names:
                if not g:
                    continue
                genre_id = _get_or_create_genre_id(cur, g)
                cur.execute(
                    """
                    INSERT INTO vinyl_genres (vinyl_id, genre_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (vinyl_id, genre_id),
                )
            return vinyl_id


def search_vinyls(
    title: Optional[str],
    author: Optional[str],
    genre: Optional[str],
    price_min: Optional[float],
    price_max: Optional[float],
) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    v.id,
                    v.title,
                    v.price,
                    a.name AS artist_name,
                    STRING_AGG(DISTINCT g.name, ', ') AS genres
                FROM vinyls v
                JOIN artists a ON a.id = v.artist_id
                LEFT JOIN vinyl_genres vg ON vg.vinyl_id = v.id
                LEFT JOIN genres g ON g.id = vg.genre_id
                WHERE
                    (%(title)s IS NULL OR v.title ILIKE '%%' || %(title)s || '%%')
                    AND (%(author)s IS NULL OR a.name ILIKE '%%' || %(author)s || '%%')
                    AND (%(genre)s IS NULL OR EXISTS (
                        SELECT 1
                        FROM vinyl_genres vg2
                        JOIN genres g2 ON g2.id = vg2.genre_id
                        WHERE vg2.vinyl_id = v.id
                          AND g2.name ILIKE '%%' || %(genre)s || '%%'
                    ))
                    AND (%(price_min)s IS NULL OR v.price >= %(price_min)s)
                    AND (%(price_max)s IS NULL OR v.price <= %(price_max)s)
                GROUP BY v.id, v.title, v.price, a.name
                ORDER BY v.id
                """,
                {
                    "title": title or None,
                    "author": author or None,
                    "genre": genre or None,
                    "price_min": price_min,
                    "price_max": price_max,
                },
            )
            return list(cur.fetchall())


def get_vinyl_detail(vinyl_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    v.id,
                    v.title,
                    v.price,
                    v.description,
                    v.cover_url,
                    a.name AS artist_name,
                    STRING_AGG(DISTINCT g.name, ', ') AS genres
                FROM vinyls v
                JOIN artists a ON a.id = v.artist_id
                LEFT JOIN vinyl_genres vg ON vg.vinyl_id = v.id
                LEFT JOIN genres g ON g.id = vg.genre_id
                WHERE v.id = %s
                GROUP BY v.id, v.title, v.price, v.description, v.cover_url, a.name
                """,
                (vinyl_id,),
            )
            return cur.fetchone()

