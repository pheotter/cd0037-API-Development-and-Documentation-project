import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app('testing')
        self.client = self.app.test_client

    def tearDown(self):
        """Executed after reach test"""
        pass

    # Categories
    def test_get_paginated_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_categories"])

    # Questions
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_questions"])

    # Questions's invalid page number
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    # Delete a question
    def test_delete_question(self):
        newQuestion = Question("Q5", "A5", 1, 2)
        newQuestion.insert()
        new_id = newQuestion.id
        questionsBeforeDelete = len(Question.query.all())
        res = self.client().delete(f'/questions/{new_id}')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == new_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], new_id)
        self.assertEqual(data["total_questions"], questionsBeforeDelete - 1)
        self.assertTrue(data["questions"])
        self.assertEqual(question, None)

    # Delete a quesion that does not exist
    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    # Create a new question
    def test_create_new_question(self):
        new_q = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1,
            'difficulty': 2
        }
        questionsBeforeCreate = len(Question.query.all())
        res = self.client().post("/questions", json=new_q)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"], True)
        self.assertEqual(data["total_questions"], questionsBeforeCreate + 1)

    # Create a new question but missing some fields
    def test_400_create_question_but_any_field_is_missed(self):
        new_q = {
            'question': 'new_question',
            'answer': 'new_answer',
            'difficulty': 2
        }
        questionsBeforeCreate = len(Question.query.all())
        res = self.client().post("/questions", json=new_q)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    # Search questions by a search term
    def test_search_questions(self):
        res = self.client().post(
            "/questions/search",
            json={
                "searchTerm": "wh"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    # Search questions but mssing a search term
    def test_400_search_questions_without_searh_term(self):
        res = self.client().post("/questions/search")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    # Get questions from a category
    def test_get_specific_questions(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], 1)

    # Get questions from a category that does not exist
    def test_404_questions_from_category_does_not_exist(self):
        res = self.client().get("/categories/10000/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    # Create a category
    def test_create_category(self):
        categoriesBeforeCreate = len(Category.query.all())
        res = self.client().post("/categories", json={"type": "Novel"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["categories"])
        self.assertEqual(data["total_categories"], categoriesBeforeCreate + 1)

    # Create a category but missing the type
    def test_400_create_category_without_type(self):
        res = self.client().post("/categories", json={"id": 1})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    # Play quizzes
    def test_play_quizzes(self):
        res = self.client().post(
            "/quizzes",
            json={
                "quiz_category": {
                    "id": 1,
                    "type": "Science"},
                "previous_questions": [5]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    # Play quizzes but missing quiz_category or previous_questions
    def test_400_play_quizzes_missing(self):
        res = self.client().post("/quizzes", json={"previous_questions": [5]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
