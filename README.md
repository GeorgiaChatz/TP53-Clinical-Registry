# TP53 Clinical Registry — complete Streamlit demonstration

Based on the field headings in your uploaded TP53 spreadsheet. Original clinical records were not copied into this package. Fictional sample patients only.

## Deploy to Streamlit Community Cloud

1. Upload `app.py`, `db.py`, `db_postgres.py`, `db_sqlite.py`, `field_schema.json`, `requirements.txt`, `.gitignore`, and optionally README.md to the **root** of your GitHub repository. Do not upload a ZIP itself. Replace the old files; don't leave nested folders or old versions.
2. Deploy main file `app.py` on Streamlit Community Cloud. Choose Python 3.11 or 3.12 if offered.
3. In Streamlit Cloud, open your app **Settings → Secrets** and add:

   ```toml
   DATABASE_URL = "postgresql://postgres.PROJECT_REFERENCE:URL_ENCODED_PASSWORD@YOUR_SESSION_POOLER_HOST:5432/postgres?sslmode=require"
   ```

   Obtain **actual** user, host, port from Supabase's **Connect → Connection string → Session pooler**. Do not use the localhost address or Supabase API keys. If Supabase URI already has query parameters, append `&sslmode=require` rather than a second `?`. Never share this credential or commit it to GitHub.
4. Save Secrets and **Reboot app**. Use app Logs to see any install or connection errors.
5. Go to Supabase **SQL Editor** and run `SELECT patient_id, diagnosis, center FROM public.patients ORDER BY patient_id;` after the app starts. Add a fictional patient in Streamlit, and confirm it appears in Supabase.

### Common deployment errors
- `No module named 'dotenv'`: deploy the included `requirements.txt` at the repository root.
- `No module named 'psycopg'`: deploy the included `requirements.txt` with `psycopg[binary]` and reboot.
- `No module named 'db_postgres'`: upload `db_postgres.py` to the same directory as `app.py`.
- Database connection timeout: choose **Session pooler**, not Direct IPv6-only. Check connection URI and database password.
- `invalid password`: reset your Supabase database password, then update Streamlit Secrets. URL-encode special characters.
- If `DATABASE_URL` isn't set, the app falls back to SQLite for demonstration; data on Streamlit Cloud is **not guaranteed to persist**.

## Run locally

Install Python 3.11/3.12 and run `start_windows.bat`, or use:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Optionally copy `.env.example` to `.env` and put your local PostgreSQL connection string in it. Without `DATABASE_URL`, local SQLite will be used.

## Features

- Sidebar navigation: dashboard, patient registry, registration, export; patient-specific clinical sections
- All original workbook clinical section headings represented in `field_schema.json`
- Repeated treatment episodes and molecular follow-up measurements
- Searchable patients, history timeline, molecular VAF trend, change log
- SQLite local demo or PostgreSQL/Supabase persistent storage via `DATABASE_URL`
- Tables created automatically: `patients`, `section_entries`, `audit_events`

## Security

**Fictional data only.** The prototype has no authentication or per-user permissions, no approved clinical audit trail, no institutional data governance, and no verified clinical scoring or validation. Do not store real patient information or use it for decisions about care. Before real deployment, add individual authentication, authorization, auditability, encrypted connections, backup/restore process, and institutional/GDPR review. Change any DB password previously shared in a chat or screenshot.
