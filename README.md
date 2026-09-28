# Samvidhan

Samvidhan is a Django website for learning about the Constitution of India. It includes educational pages, an AI-generated Constitution quiz, a user survey, and a staff-only survey results dashboard.

## Features

- Educational pages about Fundamental Rights and Duties, constitutional values, articles, cases, crimes, freedom fighters, and helplines.
- Account registration and password login, plus Google sign-in.
- Login required to take the quiz or submit a survey.
- A fresh set of 10 multiple-choice questions is requested from Gemini when the quiz page opens. Quiz answers are sent to Gemini for scoring; the answer key stays in the server-side session and the returned score is checked against it.
- Survey responses are saved to SQLite. Recorded audio is stored in the database (up to 8 MB per recording); it is not uploaded to Cloudinary.
- Survey results and saved audio playback are restricted to staff accounts. Staff can also manage submissions through Django Admin.
- A survey thank-you page appears after submission and returns the user to the home page after a short delay.

## Technology

- Python and Django 6.1.1
- SQLite
- HTML, CSS, and vanilla JavaScript
- Tailwind CSS CDN on selected pages
- Google OAuth and Gemini API (server-side requests)

## Local setup (Windows PowerShell)

Use a Python version supported by Django 6.1.1.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set the credentials described below. Then initialize the database and create an administrator account:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Start the development server:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Open <http://127.0.0.1:8000/>. After changing `.env`, stop and restart the server so Django loads the updated values.

## Environment configuration

`.env.example` lists the required variable names. Keep real credentials in the ignored `.env` file; do not commit or share it.

| Variable | Purpose |
| --- | --- |
| `GOOGLE_CLIENT_ID` | OAuth client ID for Google sign-in |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_REDIRECT_URI` | Local callback, normally `http://127.0.0.1:8000/accounts/google/callback/` |
| `GEMINI_API_KEY` | API key used by Django for quiz generation and scoring |
| `GEMINI_MODEL` | Gemini model name; the current example uses `gemini-3.8-flash` |

### Google sign-in setup

Create a **Web application** OAuth client in Google Cloud. For local development, configure this authorized JavaScript origin:

```text
http://127.0.0.1:8000
```

and this authorized redirect URI:

```text
http://127.0.0.1:8000/accounts/google/callback/
```

Copy the client ID and secret into `.env`. If the OAuth app is in testing mode, add the Google accounts that need to sign in as test users. For deployment, configure the deployed domain and callback URL in Google Cloud and update `GOOGLE_REDIRECT_URI` accordingly.

### Gemini quiz setup

Create a Gemini API key and put it in `.env` as `GEMINI_API_KEY=...`. The key is sent only from Django to Google; it is not included in quiz-page JavaScript. The quiz makes a Gemini request when it loads and another when the user submits answers. Requests can use API quota. Temporary Gemini `503` responses are retried automatically up to three times.

## Main routes

| Route | Access | Description |
| --- | --- | --- |
| `/` | Public | Home page |
| `/accounts/register/` | Public | Create an account |
| `/accounts/login/` | Public | Sign in with password or Google |
| `/accounts/logout/` | Signed in | Log out |
| `/quiz/` | Signed in | Generate and take a Constitution quiz |
| `/quiz/api/generate/` | Signed in, POST | Request a new set of questions |
| `/quiz/api/score/` | Signed in, POST | Submit quiz answers for scoring |
| `/survey/` | Signed in | Submit a survey response and optional audio |
| `/survey/thank-you/` | Public | Submission confirmation |
| `/results/` | Staff | View survey results and response reports |
| `/results/audio/<response_id>/` | Staff | Play an audio response saved in the database |
| `/admin/` | Staff | Django administration |

The educational content is served from `frontend/` through Django routes. Account and result templates are in `templates/`, and shared styles and assets are in `static/`.

## Data and access

Survey submissions are stored as `SurveyResponse` records in `db.sqlite3`. The results dashboard uses those records and calculates summary values from the database. Create a staff user with `createsuperuser` to access `/results/` and `/admin/`; regular accounts cannot access the results dashboard or audio endpoint.

The project `.gitignore` excludes `.env`, the local SQLite database, Python bytecode, and the virtual environment.
