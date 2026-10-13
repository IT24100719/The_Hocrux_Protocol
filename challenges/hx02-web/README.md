# HX-02 — The Chamber of Secrets (Web)

Stage 2 of The Horcrux Protocol. A research portal guards a diary; honest
knocking won't get you in, but the lock is not as careful as it looks.

**Category:** Web exploitation · **Points:** 100 · **Flag:** `HORCRUX{...}` (set from `integration.yml`)

## Target
`/chamber` on the CTF host — served by this stage's container (the `hx02-web`
service in `docker-compose.yml`).

## Skill practiced
Recognizing a weak/omittable authentication check and getting past a login
without valid credentials.

## Files in this stage
- `Dockerfile` — builds the stage's web service.
- `app/` — the Chamber portal application.

## Run
Built and served automatically by `docker compose up` (the `hx02-web` service).
The real flag is injected from `integration.yml` via the seeder.
