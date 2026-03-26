from __future__ import annotations

import os
from typing import Optional

import bcrypt
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .db import (
    add_to_cart,
    create_user,
    create_order_from_cart,
    create_vinyl,
    get_cart_count,
    get_cart_items,
    get_user_by_email,
    get_vinyl_detail,
    search_vinyls,
)
from .utils import calc_cart_total


BASE_DIR = Path(__file__).resolve().parents[2]
env_path_candidates = [BASE_DIR / ".env", BASE_DIR / "Musicstore" / ".env"]
for p in env_path_candidates:
    if p.exists():
        load_dotenv(str(p))
        break
else:
    # Fallback: try default `.env` from current working directory.
    load_dotenv()

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

app = FastAPI(title="MusicShop (Vinyl)")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "dev-secret-change-me"),
    max_age=60 * 60 * 24 * 7,  # 7 days
    same_site="lax",
    https_only=False,  # for local dev
)


def _hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def _check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _get_user_from_session(request: Request) -> Optional[dict]:
    user_id = request.session.get("user_id")
    email = request.session.get("email")
    role = request.session.get("role")
    if not user_id or not email:
        return None
    return {"id": user_id, "email": email, "role": role}


def _require_admin(request: Request) -> Optional[RedirectResponse]:
    user = _get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return None


def _cart_count_context(request: Request) -> int:
    user = _get_user_from_session(request)
    if not user:
        return 0
    return get_cart_count(user["id"])

def _parse_optional_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    v = value.strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse(url="/search")


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "cart_count": _cart_count_context(request), "error": None},
    )


@app.post("/register", response_class=HTMLResponse)
def register_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    email = (email or "").strip().lower()
    password = password or ""

    error = None
    # Minimal validation for lab tasks:
    # - email must look like email (simple check)
    # - password length
    if not email or "@" not in email or "." not in email:
        error = "Введите корректный email."
    elif len(password) < 6:
        error = "Пароль должен быть не короче 6 символов."
    else:
        existing = get_user_by_email(email)
        if existing:
            error = "Пользователь с таким email уже существует."

    if error:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "cart_count": _cart_count_context(request), "error": error},
            status_code=400,
        )

    try:
        password_hash = _hash_password(password)
        user_id = create_user(email, password_hash)
    except Exception:
        # In case of unexpected DB errors
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "cart_count": _cart_count_context(request), "error": "Ошибка регистрации."},
            status_code=500,
        )

    request.session["user_id"] = user_id
    request.session["email"] = email
    return RedirectResponse(url="/search", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "cart_count": _cart_count_context(request), "error": None},
    )


@app.post("/login", response_class=HTMLResponse)
def login_action(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    email = (email or "").strip().lower()
    password = password or ""

    error = None
    if not email or "@" not in email or "." not in email:
        error = "Неверный email."
    elif not password:
        error = "Введите пароль."

    if error:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "cart_count": _cart_count_context(request), "error": error},
            status_code=400,
        )

    user = get_user_by_email(email)
    if not user or not _check_password(password, user["password_hash"]):
        error = "Неверный email или пароль."
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "cart_count": _cart_count_context(request), "error": error},
            status_code=400,
        )

    request.session["user_id"] = user["id"]
    request.session["email"] = user["email"]
    request.session["role"] = user.get("role")
    return RedirectResponse(url="/search", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/search", response_class=HTMLResponse)
def search_page(
    request: Request,
    title: Optional[str] = None,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    price_min: Optional[str] = None,
    price_max: Optional[str] = None,
):
    price_min_f = _parse_optional_float(price_min)
    price_max_f = _parse_optional_float(price_max)
    results = search_vinyls(title, author, genre, price_min_f, price_max_f)
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "cart_count": _cart_count_context(request),
            "user": _get_user_from_session(request),
            "results": results,
            "filters": {
                "title": title or "",
                "author": author or "",
                "genre": genre or "",
                "price_min": "" if price_min_f is None else price_min_f,
                "price_max": "" if price_max_f is None else price_max_f,
            },
        },
    )


@app.get("/vinyl/{vinyl_id}", response_class=HTMLResponse)
def vinyl_detail(request: Request, vinyl_id: int):
    vinyl = get_vinyl_detail(vinyl_id)
    if not vinyl:
        raise HTTPException(status_code=404, detail="Vinyl not found")
    return templates.TemplateResponse(
        "vinyl.html",
        {
            "request": request,
            "cart_count": _cart_count_context(request),
            "user": _get_user_from_session(request),
            "vinyl": vinyl,
        },
    )


@app.post("/cart/add")
def cart_add(
    request: Request,
    vinyl_id: int = Form(...),
    quantity: int = Form(1),
):
    user = _get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    add_to_cart(user["id"], vinyl_id, quantity)
    return RedirectResponse(url="/cart", status_code=303)


@app.get("/cart", response_class=HTMLResponse)
def cart_page(request: Request):
    user = _get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    items = get_cart_items(user["id"])
    cart_count = get_cart_count(user["id"])
    total = calc_cart_total(items)
    return templates.TemplateResponse(
        "cart.html",
        {"request": request, "cart_count": cart_count, "user": user, "items": items, "total": total},
    )


@app.get("/checkout", response_class=HTMLResponse)
def checkout_page(request: Request):
    user = _get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    items = get_cart_items(user["id"])
    cart_count = get_cart_count(user["id"])
    total = calc_cart_total(items)
    return templates.TemplateResponse(
        "checkout.html",
        {
            "request": request,
            "cart_count": cart_count,
            "user": user,
            "items": items,
            "total": total,
            "error": None,
        },
    )


@app.post("/checkout")
def checkout_action(
    request: Request,
    delivery_address: str = Form(...),
    payment_method: str = Form(...),
):
    user = _get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    delivery_address = (delivery_address or "").strip()
    if payment_method not in ("card", "cash"):
        raise HTTPException(status_code=400, detail="Некорректный способ оплаты")
    if not delivery_address:
        return templates.TemplateResponse(
            "checkout.html",
            {
                "request": request,
                "cart_count": get_cart_count(user["id"]),
                "user": user,
                "items": get_cart_items(user["id"]),
                "total": 0,
                "error": "Введите адрес доставки.",
            },
            status_code=400,
        )
    order_id = create_order_from_cart(user["id"], delivery_address, payment_method)
    return RedirectResponse(url=f"/orders/{order_id}", status_code=303)


@app.get("/orders/{order_id}", response_class=HTMLResponse)
def order_created_page(request: Request, order_id: int):
    user = _get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "order_created.html",
        {"request": request, "cart_count": _cart_count_context(request), "user": user, "order_id": order_id},
    )


@app.get("/admin/vinyls/new", response_class=HTMLResponse)
def admin_new_vinyl_page(request: Request):
    redirect = _require_admin(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        "admin_new_vinyl.html",
        {"request": request, "cart_count": _cart_count_context(request), "user": _get_user_from_session(request), "error": None},
    )


@app.post("/admin/vinyls/new", response_class=HTMLResponse)
def admin_new_vinyl_action(
    request: Request,
    title: str = Form(...),
    artist_name: str = Form(...),
    genres: str = Form(""),
    price: str = Form(...),
    description: str = Form(""),
):
    redirect = _require_admin(request)
    if redirect:
        return redirect
    user = _get_user_from_session(request)

    title = (title or "").strip()
    artist_name = (artist_name or "").strip()
    description = (description or "").strip() or None
    genre_list = [g.strip() for g in (genres or "").split(",") if g.strip()]

    try:
        price_f = float(price)
    except ValueError:
        price_f = -1.0

    if not title or not artist_name or price_f < 0:
        return templates.TemplateResponse(
            "admin_new_vinyl.html",
            {
                "request": request,
                "cart_count": _cart_count_context(request),
                "user": user,
                "error": "Заполните название, автора и корректную цену.",
            },
            status_code=400,
        )

    vinyl_id = create_vinyl(title, artist_name, genre_list, price_f, description)
    return RedirectResponse(url=f"/vinyl/{vinyl_id}", status_code=303)

