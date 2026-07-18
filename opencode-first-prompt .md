# First Prompt for OpenCode (v2 — detailed)

Tell OpenCode to start fresh first:
```
Delete all existing files in this project except the venv folder. Start completely fresh.
```

Then paste this as the actual build prompt:

---

Build a Flask web app called "Study Tracker". Follow this exact structure and don't deviate from it:

**Folder structure:**
```
study-tracker/
├── app.py                  # entry point, creates and runs the Flask app
├── config.py                # app config (secret key, DB path)
├── requirements.txt
├── models.py                # SQLAlchemy models: Subject, StudySession
├── routes/
│   ├── __init__.py
│   ├── dashboard.py          # "/" route
│   ├── subjects.py           # "/subjects" CRUD routes
│   ├── sessions.py           # "/sessions" CRUD routes
│   └── stats.py              # "/stats" route
├── templates/
│   ├── base.html              # shared layout with nav bar, loads Tailwind via CDN
│   ├── dashboard.html
│   ├── subjects.html
│   ├── log_session.html
│   ├── sessions_list.html
│   └── stats.html
├── static/
│   └── (any custom CSS/JS if needed)
├── instance/
│   └── study.db              # SQLite database file (auto-created)
└── README.md
```

**Models (models.py):**
- `Subject`: id (int, PK), name (string, required), color (string, optional hex), created_at (datetime, default now)
- `StudySession`: id (int, PK), subject_id (FK → Subject.id), date (date, required), duration_minutes (int, required), notes (text, optional), created_at (datetime, default now)

**Routes needed:**
1. `GET /` — dashboard: show today's total minutes studied, this week's total, and a button linking to "Log a session"
2. `GET/POST /subjects` — list all subjects + form to add new one
3. `POST /subjects/<id>/edit` — edit a subject
4. `POST /subjects/<id>/delete` — delete a subject
5. `GET/POST /sessions/new` — form to log a new session (subject dropdown, date, duration, notes)
6. `GET /sessions` — list all sessions, with filter by subject and date range (via query params)
7. `POST /sessions/<id>/edit` — edit a session
8. `POST /sessions/<id>/delete` — delete a session
9. `GET /stats` — show total time per subject (today / this week / all-time) and a streak counter (consecutive days with ≥1 session)

**Requirements:**
- Use Flask-SQLAlchemy for the ORM
- Use Tailwind CSS via CDN script tag in `base.html` (no build step)
- All pages extend `base.html` and share a simple top nav: Dashboard | Subjects | Log Session | Sessions | Stats
- Mobile-responsive: nav should collapse or stack cleanly on small screens
- Include a `create_tables()` step that runs automatically on first launch if `study.db` doesn't exist yet
- `requirements.txt` must list exact packages needed (Flask, Flask-SQLAlchemy)
- `README.md` must include: how to create venv, install requirements, and run the app (`python app.py`), plus the URL to open (`http://localhost:5000`)

**Important constraints:**
- Do NOT use Django, FastAPI, or any other framework — Flask only
- Do NOT add authentication/login in this version — skip Flask-Login entirely for now
- Do NOT invent extra pages or features not listed above — build exactly this scope first
- Keep each route file focused only on its own resource (don't mix subject and session logic in one file)

After building, run the app yourself if possible and confirm there are no errors on `python app.py`, then tell me it's ready to test.

---

## If it still gets it wrong
Don't try to fix everything in one follow-up. Point at ONE broken thing at a time, e.g.:
> "The /stats route is missing entirely, add it now following the spec in the earlier prompt."

This keeps it from making unrelated changes while trying to fix one thing.
