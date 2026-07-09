import unittest

from bookrecommender.app import create_app
from bookrecommender.models import Book, db


class BooksRecommenderTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        self.client = self.app.test_client()

    def test_home_page_loads_seeded_catalog(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Books Recommender", response.data)
        self.assertIn(b"1984", response.data)
        self.assertIn(b"Clean Code", response.data)

    def test_books_api_can_filter_by_description(self):
        response = self.client.get("/api/books?query=surveillance")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["books"][0]["title"], "1984")

    def test_recommendations_rank_relevant_books(self):
        response = self.client.get("/api/recommendations?query=software testing")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["recommendations"][0]["title"], "Clean Code")
        self.assertGreater(payload["recommendations"][0]["score"], 0)

    def test_recommendations_require_query(self):
        response = self.client.get("/api/recommendations")
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["status"], "error")

    def test_add_book_validates_required_fields(self):
        response = self.client.post("/add_book", data={"title": "Incomplete"})
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["message"], "Missing required fields.")
        self.assertIn("author", payload["fields"])

    def test_add_and_delete_book(self):
        add_response = self.client.post(
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

        self.assertEqual(add_response.status_code, 201)
        self.assertEqual(
            add_payload["book"]["title"], "Designing Data-Intensive Applications"
        )

        book_id = add_payload["book"]["id"]
        delete_response = self.client.delete(f"/delete_book/{book_id}")
        delete_payload = delete_response.get_json()

        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_payload["status"], "success")

        with self.app.app_context():
            self.assertIsNone(db.session.get(Book, book_id))


if __name__ == "__main__":
    unittest.main()
