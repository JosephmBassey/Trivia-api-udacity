import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

load_dotenv()

database_path = os.getenv("DATABASE_URL")

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app, database_path=database_path):
    if not database_path:
        raise RuntimeError("DATABASE_URL is not configured")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)


"""
Question
"""


class Question(db.Model):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "difficulty": self.difficulty,
        }


"""
Category
"""


class Category(db.Model):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {"id": self.id, "type": self.type}
