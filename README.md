# TP53 Clinical Research Registry — local proof of concept

A **working Streamlit prototype** based on the *field names* in the supplied Excel workbook. The source workbook's **existing patient records are not imported or included in this package**. The database starts with three wholly fictional demo records.

## First-time installation (Windows)

1. Install **Python 3.11 or 3.12** from https://www.python.org/downloads/ . On Windows, check **Add Python to PATH** if offered.
2. Download and unzip `TP53_Registry_Prototype.zip` into a folder of your choice.
3. Open PowerShell or Command Prompt in the unzipped `TP53_Registry` folder.
4. Run:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

If `py` is unavailable, substitute `python` for `py` on the first command.

## First-time installation (macOS / Linux)

Install Python 3.11 or 3.12, then in Terminal:

```bash
cd /path/to/TP53_Registry
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Where is it launched?

The app runs **on your own computer** during testing. The terminal will show a `Local URL`, usually `http://localhost:8501`, which you open in Chrome, Edge, Safari, or Firefox. Keep the terminal open while using the app; press `Ctrl+C` in the terminal to stop it. No hosting account or server is required for local testing.

On first run, the app creates `data/registry_demo.sqlite3`. **The database persists between runs**. Back up this file if you want to retain your fictional tests. To reset the prototype to its initial fictional demo data, stop the app and delete `data/registry_demo.sqlite3`, then restart.

## What is included

- Dashboard with record counts
- Research ID patient creation and search
- Editable clinical sections automatically generated from the original workbook's field headings
- Unlimited molecular follow-up episodes and additional treatment episodes
- Chronological event timeline and VAF visualization for dated follow-up episodes
- Change history and CSV research export
- Local SQLite persistence, designed for later migration to PostgreSQL

## Scope, caveats, and security

**Do not enter real or identifiable patient information.** This is an unvalidated prototype: no login, access control, encryption-at-rest, validated audit trail, clinical data governance, backup automation, or approved hosting environment. It is intended for interface testing using synthetic data only. The existing patient data in the source workbook is intentionally excluded.

Some forms reproduce the original Excel labels and codes verbatim, so the research team should review/validate clinical coding and derived-variable definitions before actual use. Some legacy treatment fields are retained alongside a new unlimited 'Treatment episode' design. A future migration should consolidate these, define validated terminology, and provide robust dataset mappings and server-grade security.

For deployment: implement user authentication and authorization, PostgreSQL migrations, HTTPS, monitored backups, audit logging with named users, institution-approved hosting, privacy impact assessment as appropriate, and restore testing.

## PostgreSQL on your laptop (recommended for local development)

1. In pgAdmin connect to your local server (usually `localhost:5432`).
2. Run this SQL in the **postgres** database's Query Tool (change the demo password):

```sql
CREATE ROLE tp53_app LOGIN PASSWORD 'CHOOSE_A_DIFFERENT_STRONG_PASSWORD';
CREATE DATABASE tp53_registry OWNER tp53_app;
```

**Important:** `CREATE DATABASE` needs to run outside an explicit transaction block. pgAdmin Query Tool with autocommit works; run the two statements separately if needed. The app user owns its database so it can create its tables during this prototype.

3. Copy `.env.example` to `.env` inside this folder. Replace `YOUR_APP_PASSWORD` with the password chosen for `tp53_app`. URL-encode special characters in passwords. Keep `.env` private; it is ignored by git.
4. Double-click `start_windows.bat` (or use the Mac/Linux launch script). At startup the app automatically creates its tables and fictional sample patients inside PostgreSQL.
5. To verify data, connect in pgAdmin to `tp53_registry` and run `SELECT patient_id, diagnosis FROM public.patients;`.

**Database safety:** This prototype has no user login or production access controls and should only contain **fictional test patients**. Do not publish your `.env`, and don't expose your laptop PostgreSQL service to the public internet. Streamlit Community Cloud cannot use a localhost database on your laptop. For cloud testing with saved data, provision a separate hosted test database and configure cloud secrets without committing credentials.
