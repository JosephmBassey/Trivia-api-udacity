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

    def test_delete_question(self):
        with self.app.app_context():
            question = Question(
                question="Temporary question",
                answer="Temporary answer",
                category=1,
                difficulty=1,
            )
            question.insert()
            question_id = question.id

        response = self.client.delete(f"/questions/{question_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["deleted"], question_id)

        with self.app.app_context():
            self.assertIsNone(
                Question.query.filter(Question.id == question_id).one_or_none()
            )

    def test_delete_unknown_question_returns_404(self):
        response = self.client.delete("/questions/9999")

        self.assertEqual(response.status_code, 404)

    def test_create_question(self):
        response = self.client.post(
            "/questions",
            json={
                "question": "What is the test answer?",
                "answer": "A successful POST",
                "category": "1",
                "difficulty": "2",
            },
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])

        with self.app.app_context():
            question = Question.query.filter(
                Question.id == data["created"]
            ).one_or_none()
            self.assertIsNotNone(question)
            question.delete()

    def test_create_question_rejects_missing_fields(self):
        response = self.client.post(
            "/questions", json={"question": "Incomplete question"}
        )

        self.assertEqual(response.status_code, 422)

    def test_search_questions(self):
        response = self.client.post("/questions/search", json={"searchTerm": "title"})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertGreater(data["total_questions"], 0)
        self.assertTrue(
            all(
                "title" in question["question"].lower()
                for question in data["questions"]
            )
        )

    def test_search_questions_rejects_invalid_term(self):
        response = self.client.post("/questions/search", json={"searchTerm": None})

        self.assertEqual(response.status_code, 422)

    def test_get_questions_by_category(self):
        response = self.client.get("/categories/1/questions?page=1")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["current_category"], "Science")
        self.assertLessEqual(len(data["questions"]), 10)
        self.assertGreater(data["total_questions"], 0)
        self.assertTrue(
            all(question["category"] == 1 for question in data["questions"])
        )

    def test_get_questions_by_category_returns_404_for_empty_page(self):
        response = self.client.get("/categories/1/questions?page=1000")

        self.assertEqual(response.status_code, 404)

    def test_get_questions_by_unknown_category(self):
        response = self.client.get("/categories/9999/questions")

        self.assertEqual(response.status_code, 404)

    def test_play_quiz(self):
        response = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [20],
                "quiz_category": {"id": 0, "type": "All"},
            },
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["question"])
        self.assertNotEqual(data["question"]["id"], 20)

    def test_play_quiz_by_category(self):
        response = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [],
                "quiz_category": {"id": "1", "type": "Science"},
            },
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["question"]["category"], 1)

    def test_play_quiz_returns_none_when_complete(self):
        with self.app.app_context():
            question_ids = [question.id for question in Question.query.all()]

        response = self.client.post(
            "/quizzes",
            json={
                "previous_questions": question_ids,
                "quiz_category": {"id": 0, "type": "All"},
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()["question"])

    def test_play_quiz_rejects_invalid_request(self):
        response = self.client.post(
            "/quizzes",
            json={"quiz_category": {"id": 1}},
        )

        self.assertEqual(response.status_code, 422)

    def test_play_quiz_rejects_invalid_types(self):
        response = self.client.post(
            "/quizzes",
            json={
                "previous_questions": "not-a-list",
                "quiz_category": "not-an-object",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_play_quiz_rejects_non_object_body(self):
        response = self.client.post("/quizzes", json=[])

        self.assertEqual(response.status_code, 400)

    def test_play_quiz_rejects_unknown_category(self):
        response = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [],
                "quiz_category": {"id": 9999, "type": "Unknown"},
            },
        )

        self.assertEqual(response.status_code, 404)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
