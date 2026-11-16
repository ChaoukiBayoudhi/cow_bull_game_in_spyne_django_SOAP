# Cow bull game in Spyne Django SOAP

A Django project with SOAP services (Spyne).

## Tech stack

- Python 3
- Django
- Spyne (SOAP)
- lxml
- suds (SOAP client)
- requests
- Database: SQLite

## Project structure

- `cow_bull_game/`: project settings and root URLs
- `cb_game/`: Django app
- Tests: `cb_game/tests.py`

## URL routes

Declared in `urls.py`:

- `/blog/`
- `/cb_game/`

## How to run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

---

Author: [Chaouki Bayoudhi](https://github.com/ChaoukiBayoudhi)
