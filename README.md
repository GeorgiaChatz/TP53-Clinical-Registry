# TP53 Clinical Registry — screenshot-focused Streamlit prototype

This version starts directly on **Patient Information** with the full **WORKSPACE** and **PATIENT RECORD** sidebar. It is based on the user-approved reference screenshot, not on the sidebar-only alternative. The clinical field labels come from the supplied 9-sheet TP53 workbook. **Only the labels and guidelines are bundled; the sample patient's real clinical row is NOT included.**

## Deployment: replace previous GitHub files

1. Extract this ZIP and open the folder. Upload the **contents of the folder** to the **root** of your existing GitHub repository (where `app.py` is), not inside an extra folder.
2. In GitHub, replace the older `app.py`, `db.py`, `db_postgres.py`, `db_sqlite.py`, `field_schema.json` and `requirements.txt` with the files here. Add `guidelines.json` and the other nonsecret files.
3. In Streamlit Community Cloud, use **main file `app.py`** and reboot or redeploy from the new commit. Check deployment logs if an error appears.
4. In **App settings → Secrets**, keep a secret like:

   ```toml
   DATABASE_URL = "postgresql://USER:URL_ENCODED_PASSWORD@YOUR_SUPABASE_SESSION_POOLER_HOST:5432/postgres?sslmode=require"
   ```

   Copy the correct host and user from **Supabase → Connect → Session pooler**. Do **not** put your real secret in the GitHub repository. Make sure the Supabase database password previously shared in chat has been reset first. Never paste credentials into chat.
5. The app creates its own `patients`, `section_entries`, and `audit_events` tables in the connected database. Existing tables from earlier versions should remain compatible. The app seeds fictional `DEMO-001`, `DEMO-002`, and `DEMO-003` only if the patients table is empty.
6. Open the URL of your deployed Streamlit app. It will start on **Patient Information** for `DEMO-001` (if demo records exist); use the registry to switch patients.

## Local Windows development

Install Python 3.11/3.12, extract this folder and double-click `start_windows.bat`. Without `DATABASE_URL`, it uses `data/registry_demo.sqlite3` locally. This SQLite storage is **not durable** on Streamlit Community Cloud and is not suitable for real patient records.

## What is included

- Fixed header with TP53 branding and status badge
- Left sidebar: Dashboard, Patient Registry, Patient Information, Molecular Diagnosis, Treatment & Outcomes, Allogeneic SCT, Molecular Follow-up, Clinical Guidelines
- Compact patient ID + center side-by-side, biological sex, ECOG, comorbidities and Save draft
- Collapsible additional fields from the original spreadsheet
- Repeated treatment lines and molecular follow-up entries
- Searchable patient records and patient timeline / VAF trend
- Persistent PostgreSQL storage if Supabase `DATABASE_URL` is configured
- Auditing of saved changes, CSV export

## Verification and limitations

Python syntax compilation passed and SQLite database tests confirmed create → save → retrieve → audit. **A live Streamlit browser visual test was NOT possible in the authoring environment**, because Streamlit could not be installed there. Therefore this is a screenshot-focused approximation, not a verified pixel-perfect screenshot clone. Streamlit's sidebar and form controls differ from custom React controls.

**For fictional demonstration data only.** There is no application login or per-user audit identity. Do not use with real patient records until approved authentication, permissions, appropriate GDPR controls, backups and security review are in place.
