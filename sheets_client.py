"""Google Sheets client for AV equipment and staff shift data."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _get_sheet_config() -> dict:
    return dict(st.secrets["google_sheets"])


def _get_service_account_info() -> dict:
    return dict(st.secrets["google_service_account"])


@st.cache_resource(show_spinner=False)
def get_gspread_client() -> gspread.Client:
    """Create an authenticated gspread client from Streamlit secrets."""
    creds = Credentials.from_service_account_info(
        _get_service_account_info(),
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_equipment() -> pd.DataFrame:
    """Fetch AV equipment inventory from Google Sheets."""
    config = _get_sheet_config()
    client = get_gspread_client()
    spreadsheet = client.open_by_key(config["spreadsheet_id"])
    worksheet = spreadsheet.worksheet(config["equipment_tab"])
    records = worksheet.get_all_records()
    if not records:
        raise ValueError(f"No data found in tab '{config['equipment_tab']}'.")
    return pd.DataFrame(records)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_shifts() -> pd.DataFrame:
    """Fetch staff shift schedules from Google Sheets."""
    config = _get_sheet_config()
    client = get_gspread_client()
    spreadsheet = client.open_by_key(config["spreadsheet_id"])
    worksheet = spreadsheet.worksheet(config["shifts_tab"])
    records = worksheet.get_all_records()
    if not records:
        raise ValueError(f"No data found in tab '{config['shifts_tab']}'.")
    return pd.DataFrame(records)
