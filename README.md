# Guled Hotel Concierge

A Flask hotel information site with a chat concierge and WhatsApp order requests.

## Deploy on Render

1. Push this repository, including the files in `static/images`, to GitHub.
2. In Render, create a Blueprint and select the repository.
3. Review the web service from `render.yaml` and deploy it.
4. Confirm the deployed service's `/healthz` endpoint returns `{"status":"ok"}`.

The blueprint installs `requirements.txt`, starts the app with Gunicorn, and configures the health check. To enable order storage, add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` as private environment variables in Render. Never expose the service-role key in browser code or commit it to Git.

Before enabling order submissions, apply the SQL migration in `supabase/migrations` to your Supabase project. For local development, copy `.env.example` to `.env` and add your project URL and service-role key.

## Run locally

```powershell
python -m pip install -r requirements.txt
python app.py
```

The local development server is available at `http://127.0.0.1:5003`.

## Verify

```powershell
python -m unittest discover -s tests
```