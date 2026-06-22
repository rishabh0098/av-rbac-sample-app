"""Authentication and RBAC configuration."""

from __future__ import annotations

from collections.abc import Mapping

import streamlit as st
import streamlit_authenticator as stauth
from streamlit.errors import StreamlitSecretNotFoundError

# Pre-hashed demo passwords: tech123 / mgr123
DEMO_CREDENTIALS = {
    "usernames": {
        "tech1": {
            "email": "tech1@example.com",
            "name": "Tech One",
            "password": "$2b$12$H12Bpjtejto0FeWkAwQz4uP3QpPmlZ/b4myiyyQvAsZ/3BZA9qkHy",
        },
        "manager1": {
            "email": "manager1@example.com",
            "name": "Manager One",
            "password": "$2b$12$usISgobP0aapFgygfbi/GOcOkWP.myr5WkOq5sqFojaftpwdF.Gfu",
        },
    }
}

DEMO_ROLES = {
    "tech1": "technician",
    "manager1": "manager",
}

DEMO_COOKIE = {
    "name": "av_rbac_cookie",
    "key": "av_rbac_demo_signing_key_change_in_production",
    "expiry_days": 1,
}


def _to_plain_value(value: object):
    """Recursively convert Streamlit secrets objects to plain Python values."""
    if isinstance(value, Mapping):
        return {str(k): _to_plain_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain_value(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _get_secret_section(key: str) -> dict | None:
    """Return a secrets section when secrets.toml exists, else None."""
    try:
        if key in st.secrets:
            plain = _to_plain_value(st.secrets[key])
            if isinstance(plain, dict):
                return plain
    except StreamlitSecretNotFoundError:
        pass
    return None


def _load_credentials() -> dict:
    credentials = _get_secret_section("credentials")
    if credentials:
        return credentials
    return DEMO_CREDENTIALS


def _load_cookie_config() -> dict:
    cookie = _get_secret_section("cookie")
    if cookie:
        return cookie
    return DEMO_COOKIE


def get_role(username: str | None) -> str | None:
    """Return RBAC role for the authenticated username."""
    if not username:
        return None

    roles = _get_secret_section("roles")
    if roles and username in roles:
        return roles[username]

    return DEMO_ROLES.get(username)


def create_authenticator() -> stauth.Authenticate:
    """Create a streamlit-authenticator instance."""
    cookie = _load_cookie_config()
    return stauth.Authenticate(
        _load_credentials(),
        cookie["name"],
        cookie["key"],
        cookie.get("expiry_days", 1),
        auto_hash=False,
    )
