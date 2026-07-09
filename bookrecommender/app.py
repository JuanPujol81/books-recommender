from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

try:
    from .books import books as seed_books
    from .models import Book, db
    from .recommender import recommend_books
except ImportError:
    from books import books as seed_books
    from models import Book, db
    from recommender import recommend_books


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    database_path = Path(app.instance_path) / "books.db"

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        db.create_all()
        seed_database()

    register_routes(app)

    return app


def seed_database() -> None:
    if Book.query.first():
        return

    db.session.add_all(
        Book(
            title=book["title"],
            author=book["author"],
            genre=book["genre"],
            year=book["year"],
            description=book["description"],
        )
        for book in seed_books
    )
    db.session.commit()


def get_books(query: str = "") -> list[Book]:
    books_query = Book.query

    if query:
        pattern = f"%{query.strip()}%"
        books_query = books_query.filter(
            Book.title.ilike(pattern)
            | Book.author.ilike(pattern)
            | Book.genre.ilike(pattern)
            | Book.description.ilike(pattern)
        )

    return books_query.order_by(Book.title.asc()).all()


def parse_book_payload() -> tuple[dict, dict | None]:
    payload = request.get_json(silent=True) or request.form
    required_fields = ["title", "author", "genre", "year", "description"]
    cleaned_payload = {
        field: str(payload.get(field, "")).strip() for field in required_fields
    }
    missing_fields = [
        field for field, value in cleaned_payload.items() if not value
    ]

    if missing_fields:
        return {}, {
            "message": "Missing required fields.",
            "fields": missing_fields,
        }

    try:
        year = int(cleaned_payload["year"])
    except ValueError:
        return {}, {"message": "Year must be a valid number."}

    if year < 0 or year > 2100:
        return {}, {"message": "Year must be between 0 and 2100."}

    cleaned_payload["year"] = year
    return cleaned_payload, None


def register_routes(app: Flask) -> None:
    @app.get("/")
    def home():
        query = request.args.get("query", "").strip()
        books = get_books(query)
        recommendations = (
            recommend_books(Book.query.all(), query, limit=5) if query else []
        )

        return render_template(
            "index.html",
            books=books,
            query=query,
            recommendations=recommendations,
        )

    @app.get("/api/books")
    def list_books():
        query = request.args.get("query", "").strip()
        books = get_books(query)

        return jsonify(
            {
                "status": "success",
                "count": len(books),
                "books": [book.to_dict() for book in books],
            }
        )

    @app.get("/api/recommendations")
    def recommendations():
        query = request.args.get("query", "").strip()

        if not query:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Add a query to get recommendations.",
                    }
                ),
                400,
            )

        recommendations = recommend_books(Book.query.all(), query, limit=5)

        return jsonify(
            {
                "status": "success",
                "query": query,
                "count": len(recommendations),
                "recommendations": [
                    {
                        **recommendation.book.to_dict(),
                        "score": recommendation.score,
                        "reasons": recommendation.reasons,
                    }
                    for recommendation in recommendations
                ],
            }
        )

    @app.post("/add_book")
    def add_book():
        payload, error = parse_book_payload()

        if error:
            return jsonify(error), 400

        new_book = Book(**payload)
        db.session.add(new_book)
        db.session.commit()

        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Book '{new_book.title}' added successfully.",
                    "book": new_book.to_dict(),
                }
            ),
            201,
        )

    @app.delete("/delete_book/<int:book_id>")
    def delete_book(book_id):
        book = db.session.get(Book, book_id)

        if not book:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Book with id {book_id} was not found.",
                    }
                ),
                404,
            )

        db.session.delete(book)
        db.session.commit()

        return jsonify(
            {
                "status": "success",
                "message": f"Book '{book.title}' deleted successfully.",
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
