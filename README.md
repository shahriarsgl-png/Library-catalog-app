# Library Book Catalog

Flask + SQLAlchemy web app to manage a library catalog: add, search, edit, delete books
and mark them as borrowed or returned. Uses SQLite locally and PostgreSQL on Render
(via the `DATABASE_URL` environment variable).

## Run locally
    pip install -r requirements.txt
    python app.py
Open http://127.0.0.1:5000

## Deploy on Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Environment variables: `DATABASE_URL` (Internal Database URL), `STUDENT_NAME`, `STUDENT_ID`
