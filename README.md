# TP53 Clinical Registry — approved-layout prototype

This is a research demonstration for **synthetic records only**. It is not suitable for real patient data: there is no user authentication or production security review.

## Deploy to Streamlit Community Cloud

1. Extract this ZIP and upload the **contents** to the root of a private GitHub repository. Never upload `.env` or patient data.
2. Set Streamlit app entry point to `app.py` and requirements to root `requirements.txt`.
3. In Streamlit App Settings → Secrets, add:

```toml
DATABASE_URL = "postgresql://postgres.PROJECT:YOUR_PASSWORD@YOUR_SESSION_POOLER_HOST:5432/postgres?sslmode=require"
```

Copy the **Session pooler** connection string from Supabase Connect. Use your own credentials and URL-encode special characters in the password. Do not paste the URI into chat/GitHub.
4. Redeploy/reboot. The app creates `patients`, `section_entries`, and `audit_events` if they do not exist.
5. First page is a fictional patient's **Patient Information**, with clinical navigation on the left; use **Patient Registry** to open other patients. The sidebar's **More tools** contains New Patient and Export.

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Without `DATABASE_URL`, the app uses a local SQLite demo. Streamlit Cloud's local SQLite storage is **not persistent**; use Supabase for persistent fake-data testing.

## Important limitations

- Layout approximates the approved mockup using native Streamlit + CSS; exact pixels depend on browser and Streamlit version.
- The app has no user accounts or row-level permissions. Restrict testing to fabricated records only.
- The audit log records changes but not authenticated editor identity.
- This prototype does not provide a clinical-grade backup, migration, or security system.
