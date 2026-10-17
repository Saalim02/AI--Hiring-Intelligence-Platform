# Hirewise — AI Resume Screening Platform

Hirewise is a recruiter-focused Next.js and FastAPI workspace for securely uploading PDF resumes, extracting skills, searching candidates semantically, scoring resume/job-description fit, and ranking a shortlist.

## Architecture and data flow

The Next.js App Router frontend runs on port 3000 internally and FastAPI listens on 8001 internally. In the production Compose topology, only Nginx is published; `/api/*` is routed to FastAPI and all other requests go to Next.js. PostgreSQL is private to the Compose network. Port 8000 belongs to the separate Financial Intelligence/RAG application and is intentionally not used here.

The browser keeps the access token in sessionStorage only because the current backend returns a bearer token and has no cookie session endpoint. It is cleared when the tab/session ends and is never put in localStorage. For production, add an HttpOnly, Secure, SameSite cookie flow at the API boundary or put the frontend behind a same-origin reverse proxy.

## Local setup

1. If the ignored root `.env` or `backend/.env` does not already exist, create it from the corresponding example and replace every placeholder. Never copy an example over an existing real environment file. For Compose, the backend’s effective `DATABASE_URL` is constructed from the root `POSTGRES_*` values and uses `postgres:5432`; the Compose PostgreSQL service is bound to `127.0.0.1:5433` only for host-side local development, while production PostgreSQL remains private to the Docker network.
2. Start or preserve the existing PostgreSQL service without deleting volumes:

```bash
docker compose up -d postgres
```

3. Run the backend locally from the repository root:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

4. Configure and run the frontend:

```bash
cd frontend/my-app
cp .env.example .env.local
npm ci
npm run dev
```

Open `http://localhost:3000`. API docs are available at `http://127.0.0.1:8001/docs`.

## Confirmed API integration

The frontend uses the current contracts from the FastAPI source:

| Method | Endpoint | Use |
| --- | --- | --- |
| GET | `/health` | API health |
| POST | `/auth/signup` | JSON `{ username, email, password }` |
| POST | `/auth/login` | OAuth2 form fields `username` and `password`; returns bearer token |
| GET | `/resume/all` | Authenticated resume library |
| POST | `/resume/upload` | Authenticated multipart `file` PDF upload |
| GET | `/resume/{resume_id}` | Candidate detail |
| GET | `/resume/search/?query=...` | Semantic candidate search |
| POST | `/resume/ats-score/{resume_id}?job_description=...` | ATS score and skill gap |
| POST | `/resume/rank-candidates?job_description=...` | Candidate ranking |

There is no backend pagination, sort parameter, resume deletion endpoint, or cookie authentication endpoint today. Resume ownership is enforced for the authenticated recruiter/candidate routes; legacy resumes may remain unowned until a deliberate data-attribution policy is chosen.

## Docker and persistence

`docker compose config --quiet` must pass before starting the stack. Set `POSTGRES_PASSWORD` in the ignored root `.env`, provide `backend/.env`, and then use `docker compose up -d postgres`, followed by the explicit migration command `docker compose run --rm backend alembic upgrade head`, and finally `docker compose up -d --build`. Named volumes preserve PostgreSQL data, uploads, FAISS indexes, and the Hugging Face model cache. Never use `docker compose down -v`; the backend does not run migrations implicitly at startup.

For production, keep PostgreSQL, FastAPI, and Next.js private to the Docker network, restrict EC2 security groups to SSH from an administrator-controlled source plus 80/443, terminate TLS with Nginx and Certbot, and keep `NEXT_PUBLIC_API_BASE_URL=/api`. The checked-in Nginx configuration uses `server_name _` until a real domain is selected; HTTP-to-HTTPS and certificate setup remain server-side tasks.

## Validation

```bash
cd frontend/my-app
npm run lint
npx tsc --noEmit
npm run build

cd ../../backend
python -m compileall app
```

The backend tests use an isolated SQLite database and mock heavyweight AI/vector services. CI additionally upgrades a disposable PostgreSQL 16 service to Alembic head; it never uses a production database.

## CI/CD preparation

`.github/workflows/ci.yml` runs frontend lint, TypeScript validation, production build, dependency installation, and backend compilation on pull requests and pushes to `main`. `.github/workflows/deploy-ec2.yml` is manual-only and does not deploy during development.

Configure these GitHub Actions environment secrets in a protected `production` environment: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`, and `EC2_KNOWN_HOSTS`. The manual workflow also requires an exact verified `commit_sha` input. On the production EC2 host, check out the repository under `/home/ubuntu/hirewise`, install Docker Compose, create `.env.prod` and `backend/.env.prod` out of band with mode `600`, configure Nginx/TLS, and grant the deploy user only the permissions it needs. The workflow verifies the SSH host key, checks the server worktree is clean, preserves and verifies the existing deployment files and environment files, builds the requested revision, validates the restored Alembic revision, runs `alembic upgrade head` explicitly, and checks `/api/health`. It never removes volumes or overwrites either environment file.

## Backups, rollback, and security

Before migration, create a consistent backup set: quiesce writes or place the application in maintenance mode, run `pg_dump --format=custom` against the source database, archive the uploads and FAISS/vector volume without deleting the originals, record the model/cache strategy, and verify both archive checksums and a test restore. Restore the database first, copy uploads and vector data to the matching named volumes, set the same storage paths and secrets, then run migrations and validate user counts, resume ownership, sample file paths, and vector ID alignment. If validation fails, stop the application, preserve the failed artifacts for diagnosis, restore the database/files from the verified set, and restart the last known-good revision. A code rollback is not automatically safe after a non-backward-compatible schema migration.

Initial AWS guidance: use a current Ubuntu LTS EC2 host with an encrypted EBS volume sized for PostgreSQL, uploads, the FAISS index, and the Hugging Face model cache. Install Docker Engine and the Compose plugin, use an administrative SSH key, and do not expose PostgreSQL. Costs depend on instance class/RAM (the embedding model is memory-intensive), EBS size/IOPS, public IPv4, backups, data transfer, and optional DNS/TLS services; choose the region, instance size, and budget after measuring the model’s memory and latency locally.

Remaining risks include the current JWT/session-token design, synchronous model/embedding work inside request handlers, and the need to validate migration compatibility against a backup of the real legacy schema before production. Automated backend tests exist and CI runs them against an isolated test setup.

## Troubleshooting

- `401`: sign in again; the token is intentionally session-scoped.
- `413/415`: use a real PDF under 10 MB.
- Connection refused: confirm the resume backend is on 8001 and the Financial Intelligence app remains on 8000.
- Slow first upload: the embedding model may still be loading/downloading.
- Database errors: verify `DATABASE_URL`, PostgreSQL host port 5433, and that the existing volume was not altered.
