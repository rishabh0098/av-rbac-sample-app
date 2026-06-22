"""AV Operations Dashboard — unified spreadsheet viewer with RBAC."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from auth_config import create_authenticator, get_role
from data_loader import clear_data_cache, get_data_source_label, load_equipment, load_shifts
from device_control import VALID_COMMANDS, build_device_command

st.set_page_config(
    page_title="AV Operations Dashboard",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {display: none;}
        div[data-testid="column"] [data-testid="stForm"] {
            padding: 1.25rem 1.5rem 0.5rem;
            border: 1px solid #2D3440;
            border-radius: 12px;
            background: #161B22;
        }
        .login-title {
            text-align: center;
            margin-bottom: 0.15rem;
        }
        .login-hint {
            text-align: center;
            color: #9CA3AF;
            font-size: 0.85rem;
            margin: 0 0 1rem;
        }
        .header-role {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 0.45rem;
            padding-top: 0.85rem;
            white-space: nowrap;
            font-size: 0.95rem;
        }
        .header-role span {
            color: #9CA3AF;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

LOGIN_FIELDS = {
    "Form name": "Sign in",
    "Username": "Username",
    "Password": "Password",
    "Login": "Sign in",
}

authenticator = create_authenticator()

try:
    authenticator.login("unrendered")
except Exception as exc:
    st.error(f"Login error: {exc}")
    st.stop()

auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")
name = st.session_state.get("name")

if not auth_status:
    _, login_col, _ = st.columns([1, 1.1, 1])
    with login_col:
        st.markdown('<p class="login-title"><strong>AV Operations Dashboard</strong></p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="login-hint">AV equipment inventory & staff shift schedules</p>',
            unsafe_allow_html=True,
        )
        try:
            authenticator.login(fields=LOGIN_FIELDS, key="SignInForm")
        except Exception as exc:
            st.error(f"Login error: {exc}")
            st.stop()

        if auth_status is False:
            st.error("Invalid username or password.")
        else:
            with st.expander("Demo credentials", expanded=True):
                st.markdown(
                    "- **Technician:** `tech1` / `tech123`  \n"
                    "- **Manager:** `manager1` / `mgr123`"
                )
    st.stop()

role = get_role(username)
role_label = role.capitalize() if role else "Unknown"

title_col, actions_col = st.columns([7, 3])
with title_col:
    st.title("AV Operations Dashboard")
    st.caption(f"Signed in as **{name}** (`{username}`)")
with actions_col:
    action_left, action_right = st.columns([1.4, 1])
    with action_left:
        st.markdown(
            f'<div class="header-role"><span>Role</span> <strong>{role_label}</strong></div>',
            unsafe_allow_html=True,
        )
    with action_right:
        authenticator.logout("Logout", "main")

st.divider()

data_source = get_data_source_label()
if data_source == "bundled sample data":
    st.info("Running with bundled sample data (no Google Sheets secrets configured).")
else:
    st.success(f"Data source: **{data_source}**")

refresh_col1, _ = st.columns([1, 5])
with refresh_col1:
    if st.button("Refresh data"):
        clear_data_cache()
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
