# Backend MusicShop (FastAPI)

Здесь только серверная часть. Запускать uvicorn лучше **из корня репозитория** (`крп/`), чтобы совпадали импорты `backend.app...` и корневой `pytest.ini`.

## Переменные окружения

Ищем `.env` сначала в корне проекта, потом в `Musicstore/.env`. Нужны как минимум:

- **`DATABASE_URL`** — строка подключения к PostgreSQL (реальный пароль, не заглушка).
- **`SESSION_SECRET`** — произвольная строка для подписи cookie-сессий; в dev можно не трогать, но тогда не удивляйся, что в коде есть дефолт.

## Установка зависимостей

```bash
cd /path/to/крп
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Запуск

```bash
cd /path/to/крп
uvicorn backend.app.main:app --reload --port 8000 --reload-dir backend
```

Полезные URL: `/search`, `/register`, `/login`, `/cart`, `/checkout`, для админа после выдачи роли в БД — `/admin/vinyls/new`.

## Линтер и тесты

```bash
ruff check backend
pytest -q
```

Без `DATABASE_URL` интеграционные тесты в `test_auth_api.py` будут помечены как skipped — это ожидаемо.

## Лабораторная работа №6

В `tests/test_auth_api.py` — шесть сценариев для `POST /register` и `POST /login` (TestClient). В отчёте к Гитхабу обычно прикрепляют Issue с таблицей TC-AUTH-01 … TC-AUTH-06 и ссылкой на этот файл.
