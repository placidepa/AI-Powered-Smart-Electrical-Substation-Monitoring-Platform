# Online Dashboard With Upstash Redis

This project can run in two modes:

- Local Mode: the dashboard uses in-memory telemetry and local CSV seed data.
- Redis Online Mode: the dashboard reads and writes telemetry through Upstash Redis.

## 1. Create Upstash Redis

1. Go to https://console.upstash.com/.
2. Create a Redis database.
3. Open the database details page.
4. Copy the endpoint, port, and password/token.

## 2. Configure Local Credentials

Copy `.env.example` to `.env`, then fill in:

```env
UPSTASH_REDIS_HOST=your-upstash-endpoint.upstash.io
UPSTASH_REDIS_PORT=6379
UPSTASH_REDIS_PASSWORD=your-upstash-password
```

Never commit `.env`.

## 3. Install Redis Client

```powershell
.\venv\Scripts\python.exe -m pip install redis
```

## 4. Run the Dashboard

```powershell
.\venv\Scripts\python.exe -B dashboard\app.py
```

Open:

```text
http://127.0.0.1:8050/
```

If credentials are present, the dashboard shows `Redis Online` and stores live readings in:

```text
substation:telemetry
```

## 5. Publish Live Data

In another terminal:

```powershell
.\venv\Scripts\python.exe -B scripts\publish_live_data.py
```

This simulates an industrial data gateway publishing one telemetry reading per second.

## 6. Hosting Online

When deploying to Render, Railway, Azure, or another host, add the same variables as environment variables:

```text
UPSTASH_REDIS_HOST
UPSTASH_REDIS_PORT
UPSTASH_REDIS_PASSWORD
```

Then run the dashboard with:

```powershell
python -B dashboard/app.py
```
