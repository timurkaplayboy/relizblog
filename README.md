# RelizBlog

RelizBlog is a Django project for release news, blog posts, announcements, user profiles, and subscriptions.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Generate a real `SECRET_KEY` for `.env` before sharing or deploying the project:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

For local email notifications, the project uses Django's console email backend by default.
Set `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`, and `SITE_URL` in `.env` before deploying.

## GitFlow

The repository uses:

- `main` for stable releases.
- `develop` for active integration.
- `feature/*` for new tasks.
- `release/*` for release preparation.
- `hotfix/*` for urgent production fixes.
