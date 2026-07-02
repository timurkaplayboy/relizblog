# RelizBlog

RelizBlog is a Django project for release news, blog posts, announcements, user profiles, and subscriptions.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## GitFlow

The repository uses:

- `main` for stable releases.
- `develop` for active integration.
- `feature/*` for new tasks.
- `release/*` for release preparation.
- `hotfix/*` for urgent production fixes.
