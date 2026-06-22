"""Authentication and RBAC configuration."""

from __future__ import annotations

import streamlit as st
import streamlit_authenticator as stauth

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


def _load_credentials() -> dict:
    if "credentials" in st.secrets:
        return dict(st.secrets["credentials"])
    return DEMO_CREDENTIALS


def _load_cookie_config() -> dict:
    if "cookie" in st.secrets:
        return dict(st.secrets["cookie"])
    return DEMO_COOKIE


def get_role(username: str | None) -> str | None:
    """Return RBAC role for the authenticated username."""
    if not username:
        return None

    if "roles" in st.secrets and username in st.secrets["roles"]:
        return st.secrets["roles"][username]

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
