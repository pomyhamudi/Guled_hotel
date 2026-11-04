# Guled Hotel Concierge

A Flask hotel information site with a chat concierge and WhatsApp order requests.

## Deploy on Vercel with Neon

1. Push this repository, including the files in `static/images`, to GitHub.
2. In Vercel, import the repository and add a Neon database from the Storage/Marketplace integrations.
3. Add the Neon connection string as the server-side `DATABASE_URL` environment variable in Vercel. Use the pooled connection string for a serverless deployment; never expose it with a `NEXT_PUBLIC_` prefix or in browser code.
4. In the Neon SQL Editor, run [`db/schema.sql`](db/schema.sql) to create the order-request table and index.
5. Deploy the project and confirm its `/healthz` endpoint returns `{"status":"ok"}`.

The app stores consented order requests in Neon. Each row keeps the submitted contact details and free-text order summary, plus a pending/confirmed/completed/cancelled status and creation timestamp. Menu items and room information remain in the site code because the current site does not manage them dynamically or accept room reservations. The chatbot uses the questions and answers in [`hotel_faq.md`](hotel_faq.md) for additional hotel information. Keep `DATABASE_URL` private. For local development, copy `.env.example` to `.env` and replace its placeholder with the Neon connection string.

## Run locally

```powershell
python -m pip install -r requirements.txt
python app.py
```

The local development server is available at `http://127.0.0.1:5003`.
The database schema must be applied to Neon before order submissions can be saved.

## Verify

```powershell
python -m unittest discover -s tests
```