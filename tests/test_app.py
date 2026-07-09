import pytest

from bookrecommender.app import create_app
from bookrecommender.models import Book, db


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_home_page_loads_seeded_catalog(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Books Recommender" in response.data
    assert b"1984" in response.data
    assert b"Clean Code" in response.data


def test_books_api_can_filter_by_description(client):
    response = client.get("/api/books?query=surveillance")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "success"
    assert payload["count"] == 1
    assert payload["books"][0]["title"] == "1984"


def test_recommendations_rank_relevant_books(client):
    response = client.get("/api/recommendations?query=software testing")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "success"
    assert payload["recommendations"][0]["title"] == "Clean Code"
    assert payload["recommendations"][0]["score"] > 0


def test_recommendations_require_query(client):
    response = client.get("/api/recommendations")
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["status"] == "error"


def test_add_book_validates_required_fields(client):
    response = client.post("/add_book", data={"title": "Incomplete"})
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["message"] == "Missing required fields."
    assert "author" in payload["fields"]


def test_add_and_delete_book(client, app):
    add_response = client.post(
        "/add_book",
        data={
            "title": "Designing Data-Intensive Applications",
            "author": "Martin Kleppmann",
            "genre": "Technology",
            "year": "2017",
            "description": "Distributed systems, data models, reliability, and scalability.",
        },
    )
    add_payload = add_response.get_json()

    assert add_response.status_code == 201
    assert add_payload["book"]["title"] == "Designing Data-Intensive Applications"

    book_id = add_payload["book"]["id"]
    delete_response = client.delete(f"/delete_book/{book_id}")
    delete_payload = delete_response.get_json()

    assert delete_response.status_code == 200
    assert delete_payload["status"] == "success"

    with app.app_context():
        assert db.session.get(Book, book_id) is None
