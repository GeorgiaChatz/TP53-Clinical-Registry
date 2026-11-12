# TP53 Clinical Registry — visual Streamlit prototype

This version follows the agreed mockup: sidebar WORKSPACE and PATIENT RECORD sections, rounded forms, patient registry cards, draft saves and searchable clinical histories.

**DEMO ONLY.** It has no authentication, uses synthetic sample patient records, and must not be used with identifiable or real medical information.

## Deploy to Streamlit Community Cloud

1. Extract this ZIP. Upload **all files from inside the folder** to the root of your private GitHub repository (not the ZIP itself). Replace the previous `app.py` and supporting files.
2. Ensure the repository's `requirements.txt` contains the dependencies included here. Cloud deploy entry point: `app.py`, branch: `main`.
3. Streamlit Cloud > App settings > Secrets: configure the Supabase **Session pooler** connection URI (no credentials go in GitHub):

   ```toml
   DATABASE_URL = "postgresql://postgres.PROJECT_REF:ENCODED_PASSWORD@YOUR_POOLER_HOST:5432/postgres?sslmode=require"
   ```

   Use the exact Supabase URI/port provided by your dashboard. URL-encode reserved characters in your password. Do not share connection credentials.
4. Save settings and reboot/redeploy the app. If the Supabase password was previously shared, reset it and update this secret.
5. Open **Patient Registry**, then a fictional patient. Test **Patient Information → Save draft**, then close and reopen the record. Use **Full Clinical History** to see saved events.

## Local run

Python 3.11 or 3.12:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

With no `DATABASE_URL`, the demo uses a local SQLite database at `data/registry_demo.sqlite3`. Data on Streamlit Cloud's local filesystem is not durable; **use Supabase/PostgreSQL for cloud saves**.

To connect to local PostgreSQL instead, create a `.env` file from `.env.example` with `DATABASE_URL` and a dedicated, restricted PostgreSQL account. Never commit the `.env` file.

## Database tables

The app automatically creates `patients`, `section_entries`, and `audit_events` on PostgreSQL startup. `section_entries` stores each patient's section data and repeating molecular assessments. Save and read both use the same database connection.

Supabase SQL check:

```sql
SELECT patient_id, center, diagnosis FROM public.patients ORDER BY patient_id;
SELECT patient_id, section, episode FROM public.section_entries ORDER BY patient_id, section, episode;
```

## Limitations / next steps

The visual design is an approximation of the conversation mockup, rendered using Streamlit CSS rather than a standalone React front end. The database contains raw clinical field codes (`c2`, `c3`, etc.) mapped to their original labels in `field_schema.json`. Forms render all of the original field labels, but the initial Patient Information screen shows the most important fields first.

No per-user roles, RLS policies, medical validation, verified backup/recovery, audit user identity or compliant medical data protection have yet been implemented. Do not invite users to enter actual patient data.
