"""AV Operations Dashboard — unified spreadsheet viewer with RBAC."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from auth_config import create_authenticator, get_role
from data_loader import get_data_source_label, load_equipment, load_shifts
from device_control import VALID_COMMANDS, build_device_command

st.set_page_config(
    page_title="AV Operations Dashboard",
    page_icon="📺",
    layout="wide",
)

authenticator = create_authenticator()

try:
    authenticator.login()
except Exception as exc:
    st.error(f"Login error: {exc}")
    st.stop()

auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")
name = st.session_state.get("name")

if not auth_status:
    st.title("AV Operations Dashboard")
    st.markdown(
        "Sign in to view AV equipment inventory and staff shift schedules. "
        "Demo accounts: **tech1** / `tech123` (Technician) or **manager1** / `mgr123` (Manager)."
    )
    if auth_status is False:
        st.error("Username or password is incorrect.")
    else:
        st.info("Enter your credentials to continue.")
    st.stop()

role = get_role(username)

st.title("AV Operations Dashboard")
header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
with header_col1:
    st.caption(f"Signed in as **{name}** (`{username}`)")
with header_col2:
    st.metric("Role", role.capitalize() if role else "Unknown")
with header_col3:
    authenticator.logout("Logout", "main")

st.divider()

data_source = get_data_source_label()
if data_source == "bundled sample data":
    st.info("Running with bundled sample data (no Google Sheets secrets configured).")
else:
    st.success(f"Data source: **{data_source}**")

refresh_col1, refresh_col2 = st.columns([1, 5])
with refresh_col1:
    if st.button("Refresh data"):
        load_equipment.clear()
        load_shifts.clear()
        st.rerun()

equipment_df = load_equipment()
shifts_df = load_shifts()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("AV Equipment Inventory")
    st.dataframe(equipment_df, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("Staff Shift Schedules")
    st.dataframe(shifts_df, use_container_width=True, hide_index=True)

if role == "manager":
    st.divider()
    st.subheader("Device Control")
    st.markdown(
        "Select a device and command to generate a JSON control payload "
        "simulating a direct AV device instruction."
    )

    if "command_log" not in st.session_state:
        st.session_state["command_log"] = []

    device_ids = equipment_df["device_id"].dropna().astype(str).tolist()
    if not device_ids:
        st.warning("No devices available in the equipment inventory.")
    else:
        control_col1, control_col2, control_col3 = st.columns(3)
        with control_col1:
            selected_device = st.selectbox("Device", device_ids)
        with control_col2:
            selected_command = st.selectbox("Command", list(VALID_COMMANDS))
        with control_col3:
            volume_level = st.number_input(
                "Volume level",
                min_value=0,
                max_value=100,
                value=50,
                disabled=selected_command != "volume_set",
            )

        if st.button("Trigger Device Command", type="primary"):
            parameters = {}
            if selected_command == "volume_set":
                parameters = {"level": int(volume_level)}

            payload = build_device_command(
                command=selected_command,
                device=selected_device,
                requested_by=username or "unknown",
                parameters=parameters,
            )
            st.session_state["command_log"].insert(0, payload)
            st.toast("Device command generated.")
            st.markdown("**Generated JSON payload:**")
            st.json(payload)

    if st.session_state["command_log"]:
        st.markdown("**Command history (this session):**")
        history_df = pd.DataFrame(st.session_state["command_log"])
        st.dataframe(history_df, use_container_width=True, hide_index=True)

elif role == "technician":
    st.divider()
    st.caption(
        "Technician view: read-only access. Device commands require Manager role."
    )
else:
    st.warning("Your account does not have a recognized role.")
