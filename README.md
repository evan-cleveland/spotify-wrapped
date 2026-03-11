# spotify-wrapper

A Django app that generates a Spotify Wrapped-style experience from a user's Spotify data.

## Stack

- Python
- Django
- Spotify Web API
- SQLite for local development
- Optional Google Gemini integration for AI-generated blurbs

## Prerequisites

- Python 3.11+ recommended
- A Spotify developer app with a valid redirect URI
- A Gemini API key if you want AI responses enabled

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.
4. Replace every placeholder with real values.
5. Run migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

## Environment Variables

The app reads configuration from a `.env` file in the project root.

Required:

- `DJANGO_SECRET_KEY`
- `CLIENT_ID`
- `CLIENT_SECRET`
- `REDIRECT_URI`

Optional:

- `DEBUG` (`True` or `False`)
- `ALLOWED_HOSTS` (comma-separated)
- `GOOGLE_GEMINI_KEY`

Example:

```env
DJANGO_SECRET_KEY=your-django-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CLIENT_ID=your-spotify-client-id
CLIENT_SECRET=your-spotify-client-secret
REDIRECT_URI=http://localhost:8000/callback/
GOOGLE_GEMINI_KEY=your-gemini-key
```

## Spotify Configuration

In your Spotify developer dashboard, add the same callback URL you use for `REDIRECT_URI`.

For local development:

```text
http://localhost:8000/callback/
```

## GitHub Readiness

The repository is set up so local-only files should stay out of source control:

- `.env` and other local env files are ignored
- SQLite database files are ignored
- virtual environments, editor folders, caches, and OS junk files are ignored

Before pushing, verify that you are not committing:

- real API keys or secrets
- local database files
- IDE configuration

## Security Notes

- Secrets should only live in `.env`, never in committed source files
- The Spotify client secret is used server-side only
- Rotate any previously exposed Spotify, Gemini, or Django secrets before reusing this project publicly
