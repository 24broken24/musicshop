# Backend (FastAPI) для MusicShop

## Запуск (локально)

1) Убедись, что PostgreSQL запущен и доступна БД `MusicShopDB`.

2) Проверь переменные окружения в файле `Musicstore/.env` (в твоём репозитории уже есть `.env`, но там должен быть реальный пароль PostgreSQL).

3) Установка зависимостей:

```bash
cd ~/Desktop/крп/backend
python3 -m pip install -r requirements.txt
```

4) Запуск сервера:

```bash
cd ~/Desktop/крп
uvicorn backend.app.main:app --reload --port 8000
```

После запуска открой:
- `http://localhost:8000/register`
- `http://localhost:8000/login`
- `http://localhost:8000/search`

