# AV Operations Dashboard

A Streamlit sample app for the NYU Cloud and API Automation Developer application. It unifies **AV Equipment Inventory** (Spreadsheet A) and **Staff Shift Schedules** (Spreadsheet B) in one dashboard and enforces **Role-Based Access Control (RBAC)** with simulated JSON device control for Managers.

## Live Demo

**GitHub repo:** https://github.com/rishabh0098/av-rbac-sample-app

**Live Streamlit URL:** `https://YOUR-APP-NAME.streamlit.app` *(replace after Streamlit Cloud deployment)*

**View source spreadsheets (read-only):** [AV Operations Data](https://docs.google.com/spreadsheets/d/1PpB9EiGQNAhW9G0dVCTMjLKvX3NKFc__pkMpjlL99bM/edit?usp=sharing)

| Role | Username | Password | Access |
|------|----------|----------|--------|
| Technician | `tech1` | `tech123` | View spreadsheet data only |
| Manager | `manager1` | `mgr123` | View data + trigger device commands |

## How to Test Roles

1. Open the live demo URL (or run locally — see below).
2. Log in as **tech1** / `tech123`:
   - You should see both data tables (equipment + shifts).
   - You should **not** see a "Device Control" section or "Trigger Device Command" button.
3. Log out, then log in as **manager1** / `mgr123`:
   - You should see both data tables.
   - You should see the **Device Control** panel with device/command selectors.
4. As Manager, click **Trigger Device Command**.
5. A JSON payload appears below the button (see next section).

## Where to View the Generated JSON Payload

After logging in as **manager1** and clicking **Trigger Device Command**:

- The payload renders immediately in the **Generated JSON payload** block (`st.json`).
- Example output:

```json
{
  "command": "power_on",
  "device": "projector_1",
  "parameters": {},
  "requested_by": "manager1",
  "timestamp": "2026-06-22T14:30:00Z"
}
```

- All commands triggered in the session are also listed in the **Command history** table below the panel.

## Data Sources

The app supports two data modes automatically:

| Mode | When | Source |
|------|------|--------|
| Demo | No Google secrets configured | Bundled CSVs in `sample_data/` |
| Live | Google secrets configured | Google Sheets API |

**View-only Google Sheet:** [AV Operations Data](https://docs.google.com/spreadsheets/d/1PpB9EiGQNAhW9G0dVCTMjLKvX3NKFc__pkMpjlL99bM/edit?usp=sharing) — contains tabs `AV Equipment Inventory` and `Staff Shift Schedules`.

## Project Structure

```
app.py              # Streamlit UI, login, RBAC gating
auth_config.py      # Credentials and role mapping
data_loader.py      # CSV fallback + Google Sheets routing
sheets_client.py    # Google Sheets API client
device_control.py   # JSON payload builder
sample_data/        # Mock spreadsheet data (CSV)
```

## Run Locally (Demo Mode)

No Google credentials required. Uses bundled sample CSVs.

```bash
cd "/Users/rishabhkumar/NYU Cloud and API Automation Developer Application Sample App"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` and log in with the demo credentials above.

## Optional: Connect Google Sheets Locally

1. Copy the secrets template:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Follow **Manual Setup: Google Sheets** below to get your service account and spreadsheet ID.
3. Fill in `.streamlit/secrets.toml` (never commit this file).
4. Restart the app — it will show "Data source: Google Sheets".

---

## Manual Setup (Steps You Must Complete)

These steps require your Google and Streamlit accounts in a browser. They cannot be automated.

### A. Google Sheets (for live data on hosted app)

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project → enable **Google Sheets API**.
3. Go to **IAM & Admin → Service Accounts** → create a service account.
4. Create a JSON key for the service account and download it.
5. Create a Google Spreadsheet with two tabs:
   - `AV Equipment Inventory` — columns: `device_id`, `device_name`, `type`, `location`, `status`, `last_maintenance`
   - `Staff Shift Schedules` — columns: `staff_id`, `name`, `role`, `shift_date`, `start_time`, `end_time`, `location`
   - Seed data from `sample_data/av_equipment.csv` and `sample_data/staff_shifts.csv`.
6. **Share** the spreadsheet with the service account email (from the JSON `client_email` field) as **Viewer**.
7. Copy the **Spreadsheet ID** from the URL:
   `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
8. Optionally set the sheet to "Anyone with the link can view" and add the URL to this README.

### B. Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (see repo URL after deployment).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Click **Create app** → select this repo, branch `main`, main file `app.py`.
4. Open **Advanced settings → Secrets** and paste the contents of `.streamlit/secrets.toml.example`, filling in:
   - `[google_service_account]` — all fields from your downloaded JSON key
   - `[google_sheets]` — your spreadsheet ID and tab names
   - `[credentials]` — pre-hashed passwords (example file already includes working hashes for `tech123` / `mgr123`)
   - `[roles]` — `tech1 = "technician"`, `manager1 = "manager"`
   - `[cookie]` — set `key` to a random string (32+ characters)
5. Click **Deploy** and wait for the build to finish.
6. Copy the live URL and update the **Live Demo** section at the top of this README.

### C. Regenerate Password Hashes (optional)

If you change demo passwords, generate new bcrypt hashes inside the venv:

```bash
source .venv/bin/activate
python -c "import streamlit_authenticator as stauth; h = stauth.Hasher(); print(h.hash_list(['your_new_password']))"
```

Paste the hash into Streamlit Cloud secrets and/or local `secrets.toml`.

## Requirements Met

- **Unified UI:** Fetches and displays AV Equipment Inventory + Staff Shift Schedules together.
- **RBAC:** Technician (view only) vs Manager (view + device commands).
- **JSON device control:** Manager "Trigger Device Command" outputs a valid JSON payload simulating AV device control.
- **Spreadsheet integration:** Google Sheets when configured; bundled CSV demo data as fallback.
- **Recruiter-friendly:** Live Streamlit Cloud URL works with zero local setup.

## License

Sample application for job submission purposes.
