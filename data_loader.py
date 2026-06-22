"""Data loading with Google Sheets or bundled CSV fallback."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

SAMPLE_DATA_DIR = Path(__file__).parent / "sample_data"
EQUIPMENT_CSV = SAMPLE_DATA_DIR / "av_equipment.csv"
SHIFTS_CSV = SAMPLE_DATA_DIR / "staff_shifts.csv"


def has_google_secrets() -> bool:
    """Return True when Google Sheets credentials are configured."""
    try:
        return (
            "google_service_account" in st.secrets
            and "google_sheets" in st.secrets
            and st.secrets["google_sheets"].get("spreadsheet_id")
            not in (None, "", "YOUR_SPREADSHEET_ID")
        )
    except StreamlitSecretNotFoundError:
        return False


def get_data_source_label() -> str:
    """Human-readable label for the active data source."""
    return "Google Sheets" if has_google_secrets() else "bundled sample data"


@st.cache_data(ttl=300, show_spinner=False)
def load_equipment() -> pd.DataFrame:
    """Load AV equipment inventory from Sheets or local CSV."""
    if has_google_secrets():
        try:
            from sheets_client import fetch_equipment

            return fetch_equipment()
        except Exception as exc:
            st.warning(
                f"Could not load equipment from Google Sheets ({exc}). "
                "Falling back to bundled sample data."
            )
    return pd.read_csv(EQUIPMENT_CSV)


@st.cache_data(ttl=300, show_spinner=False)
def load_shifts() -> pd.DataFrame:
    """Load staff shift schedules from Sheets or local CSV."""
    if has_google_secrets():
        try:
            from sheets_client import fetch_shifts

            return fetch_shifts()
        except Exception as exc:
            st.warning(
                f"Could not load shifts from Google Sheets ({exc}). "
                "Falling back to bundled sample data."
            )
    return pd.read_csv(SHIFTS_CSV)


def clear_data_cache() -> None:
    """Clear cached spreadsheet data so the next load fetches fresh values."""
    load_equipment.clear()
    load_shifts.clear()
    if has_google_secrets():
        from sheets_client import fetch_equipment, fetch_shifts

        fetch_equipment.clear()
        fetch_shifts.clear()
