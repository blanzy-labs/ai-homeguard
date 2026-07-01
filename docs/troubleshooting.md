# Troubleshooting

## Docker Is Not Running

Start Docker Desktop or the Docker daemon, then retry:

```bash
docker compose build
```

## Port 8000 or 5173 Is Already In Use

Stop the process using the port or adjust the port mapping in `docker-compose.yml`.

## uv Is Missing

Install uv using the official uv installation instructions or Homebrew, then confirm:

```bash
uv --version
```

## pnpm Is Missing

Enable pnpm with Corepack or install it through the approved local package manager, then confirm:

```bash
pnpm --version
```

## Frontend Cannot Reach Backend

Confirm the backend is running:

```bash
curl http://localhost:8000/health
```

If the backend is on a non-default URL, set `VITE_API_BASE_URL` for the frontend.

## Backend Health Check Fails

Run the backend directly and inspect the terminal output:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Then retry:

```bash
curl http://localhost:8000/health
```

## .env Is Not Loaded

Slice 1 does not require a `.env` file. If you add one locally, keep it out of git and compare it with `.env.example`.

## Browser Shows a Stale Frontend

Hard-refresh the browser tab, stop and restart the Vite dev server, or clear the browser cache for `localhost:5173`.
