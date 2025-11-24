# Repository Guidelines

## Project Structure & Modules
- Root holds repo metadata (`README.md`, `repository.json`) and this guide.
- Add-ons live in subfolders; currently only `meetpalen-golfhoogte/` (Dockerfile, `config.json`, `app/main.py`, `rootfs/run.sh`, add-on README).
- No tests directory yet; add-on code is in `app/` and runs inside HA Supervisor.

## Build, Run, and Development
- Standard HA add-on build flow happens via Home Assistant Supervisor; locally, keep files ASCII and runnable on Alpine Python.
- To rebuild/publish via HA: Add-on Store → ⋮ → Reload → open add-on → Update/Restart.
- For quick local syntax check: `python3 -m py_compile app/main.py` (run inside `meetpalen-golfhoogte`).

## Coding Style & Naming
- Python: 4-space indent; prefer small, pure helpers; keep functions single-responsibility.
- Config keys snake_case; MQTT topics already use the HA discovery convention (`homeassistant/<type>/...`).
- Avoid non-ASCII unless required by source data; log messages in concise English/Dutch as appropriate.

## Testing Guidelines
- No automated test suite yet. When adding logic, at minimum run `python3 -m py_compile app/main.py`.
- If you add tests, colocate under `meetpalen-golfhoogte/tests/` and document commands in this file.

## Commit & PR Guidelines
- Commits: short imperative subject, e.g., “Add MQTT setup notification” or “Detail HA 2025 install steps”.
- Group related changes (code + docs together). Avoid touching unrelated add-ons.
- PRs (if used): include a brief summary, user impact (e.g., new config fields, required HA steps), and screenshots/log snippets if UI- or UX-relevant.

## Security & Configuration Tips
- Do not hardcode credentials; brokers should be configured via add-on options (`mqtt_username`/`mqtt_password`).
- Keep polling defaults respectful (≥600s) to avoid hammering the Rijkswaterstaat endpoint.
- When adding dependencies, pin minimal versions in `requirements.txt` and ensure they work on Alpine.

## Agent-Specific Notes
- Network access may be restricted; push/pull via `git@github.com:whizzrd/broos-ha-addons.git`.
- HA-side actions happen via the UI/Supervisor; avoid editing HA data paths unless explicitly instructed. 
