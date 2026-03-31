from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="Нужен DATABASE_URL (PostgreSQL) для интеграционных тестов auth",
)

client = TestClient(app)


def _unique_email(prefix: str = "pytest") -> str:
    return f"{prefix}_{uuid.uuid4().hex}@example.com"


class TestRegisterEndpoint:

    def test_register_success_valid_data(self) -> None:
        email = _unique_email("reg_ok")
        response = client.post(
            "/register",
            data={"email": email, "password": "secret12"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        loc = response.headers.get("location", "")
        assert loc.endswith("/search")

    def test_register_fails_when_email_already_taken(self) -> None:
        email = _unique_email("reg_dup")
        first = client.post(
            "/register",
            data={"email": email, "password": "secret12"},
            follow_redirects=False,
        )
        assert first.status_code == 303
        second = client.post(
            "/register",
            data={"email": email, "password": "otherpwd1"},
            follow_redirects=False,
        )
        assert second.status_code == 400
        assert "уже существует" in second.text


class TestLoginEndpoint:

    def test_login_success_valid_credentials(self) -> None:
        email = _unique_email("login_ok")
        password = "secret12"
        r_reg = TestClient(app).post(
            "/register",
            data={"email": email, "password": password},
            follow_redirects=False,
        )
        assert r_reg.status_code == 303
        c2 = TestClient(app)
        response = c2.post("/login", data={"email": email, "password": password}, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers.get("location", "").endswith("/search")

    def test_login_fails_user_not_found(self) -> None:
        response = client.post(
            "/login",
            data={"email": _unique_email("nosuch"), "password": "secret12"},
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert "Неверный email или пароль" in response.text

    def test_login_fails_wrong_password(self) -> None:
        email = _unique_email("login_wrong")
        TestClient(app).post(
            "/register",
            data={"email": email, "password": "rightpass1"},
            follow_redirects=False,
        )
        c = TestClient(app)
        response = c.post("/login", data={"email": email, "password": "badpassword"}, follow_redirects=False)
        assert response.status_code == 400
        assert "Неверный email или пароль" in response.text

    def test_login_fails_invalid_email_format(self) -> None:
        response = client.post(
            "/login",
            data={"email": "not_an_email", "password": "secret12"},
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert "Неверный email" in response.text
