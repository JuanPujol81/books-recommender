# Books Recommender

A small Flask application that recommends books from a local catalog using transparent content-based scoring.

The project is designed as a portfolio-ready backend/web app: it has a searchable UI, JSON API endpoints, SQLite persistence through SQLAlchemy, seed data, validation, tests, and clear setup instructions.

## Interview Summary

I built a Books Recommender with Flask, SQLite, and SQLAlchemy. The app seeds a book catalog, lets users search by title, author, genre, or description, and returns ranked recommendations using a deterministic content-matching score. It also exposes JSON endpoints for catalog search and recommendations, includes validation for create/delete actions, and has automated tests for the main user and API flows.

## Features

- Searchable book catalog.
- Content-based recommendation scoring.
- SQLite database with SQLAlchemy models.
- Seed data loaded automatically on first run.
- Browser UI for search, recommendations, adding books, and deleting books.
- JSON API endpoints for integration or testing.
- Automated tests for core flows.
- `.gitignore` excludes virtual environments, SQLite databases, and cache files.

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML/CSS
- unittest

## Project Structure

```text
.
├── bookrecommender/
│   ├── app.py                 # Flask app factory, routes, validation
│   ├── books.py               # Seed catalog
│   ├── models.py              # SQLAlchemy Book model
│   ├── recommender.py         # Content-based recommendation scoring
│   ├── static/styles.css      # UI styling
│   └── templates/index.html   # Browser UI
├── tests/test_app.py          # API and app tests
├── requirements.txt
└── README.md
```

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python -m bookrecommender.app
```

Open:

```text
http://127.0.0.1:5000
```

The SQLite database is created automatically in `instance/books.db`.

Alternative Flask CLI command:

```bash
flask --app bookrecommender.app:create_app run
```

## Run Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The tests use an in-memory SQLite database, so they do not depend on local database files.

## API Endpoints

### `GET /health`

Returns service health:

```json
{
  "status": "healthy"
}
```

### `GET /api/books`

Returns all books.

Optional query filter:

```text
/api/books?query=surveillance
```

### `GET /api/recommendations`

Returns ranked recommendations for a query:

```text
/api/recommendations?query=software testing
```

Example response shape:

```json
{
  "status": "success",
  "query": "software testing",
  "count": 1,
  "recommendations": [
    {
      "id": 10,
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "genre": "Technology",
      "year": 2008,
      "description": "...",
      "score": 2,
      "reasons": ["description match"]
    }
  ]
}
```

### `POST /add_book`

Adds a book. Accepts form data or JSON with:

- `title`
- `author`
- `genre`
- `year`
- `description`

### `DELETE /delete_book/<book_id>`

Deletes a book by id.

## Recommendation Logic

The recommendation engine is deterministic and explainable:

1. Tokenizes the user query.
2. Compares query tokens against each book's title, author, genre, and description.
3. Applies weighted scoring:
   - title matches: highest weight
   - author matches
   - genre matches
   - description matches
4. Returns the highest-scoring books with human-readable match reasons.

This keeps the project easy to review in interviews because the behavior is understandable without external services or hidden model files.

## Portfolio Notes

This project demonstrates:

- Flask app structure and app factory pattern.
- SQLAlchemy model design.
- SQLite persistence.
- API design and JSON responses.
- Input validation and error handling.
- Testable recommendation logic.
- Clean repository hygiene by excluding generated virtual environments and local database files.
