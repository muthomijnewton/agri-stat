"""Tests for Authentication API endpoints."""
import pytest
from app.models.models import User
from app.core.security import get_password_hash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LOGIN_URL = "/api/auth/login"
VERIFY_URL = "/api/auth/verify"


def _create_user(db, *, username, password, email, is_admin=False, is_active=True):
    """Insert a user with a properly hashed password and return the ORM object."""
    user = User(
        username=username,
        email=email,
        password=get_password_hash(password),
        full_name="Test User",
        is_admin=is_admin,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Login — success cases
# ---------------------------------------------------------------------------

def test_login_success(unauthenticated_client, db):
    """Valid credentials return 200 with an access token."""
    _create_user(db, username="farmer1", password="securepass", email="farmer1@test.com")

    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "farmer1", "password": "securepass"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] != ""
    assert data["token_type"] == "bearer"
    assert data["username"] == "farmer1"
    assert data["message"] == "Login successful"


def test_login_returns_user_fields(unauthenticated_client, db):
    """Login response includes id, email, full_name, and is_admin."""
    _create_user(
        db,
        username="farmer2",
        password="pass1234",
        email="farmer2@test.com",
        is_admin=False,
    )

    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "farmer2", "password": "pass1234"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "farmer2@test.com"
    assert data["is_admin"] is False
    assert isinstance(data["id"], int)


def test_login_admin_user(unauthenticated_client, db):
    """Admin users receive is_admin=True in the response."""
    _create_user(
        db,
        username="adminuser",
        password="adminpass",
        email="admin@test.com",
        is_admin=True,
    )

    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "adminuser", "password": "adminpass"},
    )

    assert response.status_code == 200
    assert response.json()["is_admin"] is True


# ---------------------------------------------------------------------------
# Login — failure cases
# ---------------------------------------------------------------------------

def test_login_wrong_password(unauthenticated_client, db):
    """Wrong password returns 401."""
    _create_user(db, username="farmer3", password="rightpass", email="farmer3@test.com")

    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "farmer3", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_nonexistent_user(unauthenticated_client):
    """Login for a username that does not exist returns 401."""
    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "ghost_user", "password": "whatever"},
    )

    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_inactive_user(unauthenticated_client, db):
    """Inactive user accounts are rejected with 403."""
    _create_user(
        db,
        username="inactive_user",
        password="pass1234",
        email="inactive@test.com",
        is_active=False,
    )

    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "inactive_user", "password": "pass1234"},
    )

    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_login_missing_username(unauthenticated_client):
    """Request body missing 'username' returns 422 Unprocessable Entity."""
    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"password": "somepassword"},
    )

    assert response.status_code == 422


def test_login_missing_password(unauthenticated_client):
    """Request body missing 'password' returns 422 Unprocessable Entity."""
    response = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "farmer1"},
    )

    assert response.status_code == 422


def test_login_empty_body(unauthenticated_client):
    """Empty request body returns 422 Unprocessable Entity."""
    response = unauthenticated_client.post(LOGIN_URL, json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Token — protected route access
# ---------------------------------------------------------------------------

def test_token_grants_access_to_protected_route(unauthenticated_client, db):
    """A token obtained from /login can be used to access a protected endpoint."""
    _create_user(db, username="farmer4", password="pass5678", email="farmer4@test.com")

    login_resp = unauthenticated_client.post(
        LOGIN_URL,
        json={"username": "farmer4", "password": "pass5678"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    protected_resp = unauthenticated_client.get(
        "/api/products",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert protected_resp.status_code == 200


def test_invalid_token_rejected(unauthenticated_client):
    """A malformed / fabricated token is rejected with 401."""
    response = unauthenticated_client.get(
        "/api/products",
        headers={"Authorization": "Bearer this.is.not.a.real.token"},
    )
    assert response.status_code == 401


def test_missing_token_rejected(unauthenticated_client):
    """No Authorization header returns 401 on protected endpoints."""
    response = unauthenticated_client.get("/api/products")
    assert response.status_code == 401


def test_malformed_auth_header_rejected(unauthenticated_client):
    """Authorization header without 'Bearer' prefix returns 401."""
    response = unauthenticated_client.get(
        "/api/products",
        headers={"Authorization": "Token some_random_value"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Verify endpoint
# ---------------------------------------------------------------------------

def test_verify_endpoint_success(unauthenticated_client, db):
    """The /verify endpoint behaves identically to /login on valid credentials."""
    _create_user(db, username="farmer5", password="verifypass", email="farmer5@test.com")

    response = unauthenticated_client.post(
        VERIFY_URL,
        json={"username": "farmer5", "password": "verifypass"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "farmer5"


def test_verify_endpoint_wrong_password(unauthenticated_client, db):
    """The /verify endpoint returns 401 for wrong credentials."""
    _create_user(db, username="farmer6", password="correctpass", email="farmer6@test.com")

    response = unauthenticated_client.post(
        VERIFY_URL,
        json={"username": "farmer6", "password": "wrongpass"},
    )

    assert response.status_code == 401
