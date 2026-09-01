import os
import unittest

from flaskr import create_app
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "password"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": self.database_path,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "TESTING": True,
            }
        )
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        response = self.client.get("/categories")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["categories"])

    def test_get_questions_is_paginated(self):
        first_page = self.client.get("/questions?page=1")
        second_page = self.client.get("/questions?page=2")
        first_data = first_page.get_json()
        second_data = second_page.get_json()

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(first_data["questions"]), 10)
        self.assertEqual(len(second_data["questions"]), 9)
        self.assertEqual(first_data["total_questions"], 19)
        self.assertIsNone(first_data["current_category"])

    def test_get_questions_returns_404_for_empty_page(self):
        response = self.client.get("/questions?page=1000")

        self.assertEqual(response.status_code, 404)

    def test_get_questions_rejects_invalid_page(self):
        response = self.client.get("/questions?page=invalid")

        self.assertEqual(response.status_code, 400)

    def test_cors_headers_are_present(self):
        response = self.client.get(
            "/categories", headers={"Origin": "http://localhost:3000"}
        )

        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"], "http://localhost:3000"
        )
        self.assertIn("GET", response.headers["Access-Control-Allow-Methods"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
