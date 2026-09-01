from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories},
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        try:
            page = int(request.args.get("page", "1"))
        except (TypeError, ValueError):
            abort(400)

        if page < 1:
            abort(400)

        selection = Question.query.order_by(Question.id)
        pagination = selection.paginate(
            page=page, per_page=QUESTIONS_PER_PAGE, error_out=False
        )
        questions = [question.format() for question in pagination.items]

        if not questions:
            abort(404)

        categories = Category.query.order_by(Category.id).all()

        return jsonify(
            {
                "success": True,
                "questions": questions,
                "total_questions": pagination.total,
                "categories": {category.id: category.type for category in categories},
                "current_category": None,
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify(
            {
                "success": True,
                "deleted": question_id,
                "total_questions": Question.query.count(),
            }
        )

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        if body is None:
            abort(400)

        question_text = body.get("question")
        answer = body.get("answer")
        category = body.get("category")
        difficulty = body.get("difficulty")

        if (
            question_text is None
            or answer is None
            or category is None
            or difficulty is None
        ):
            abort(422)

        selected_category = Category.query.filter(Category.id == category).one_or_none()
        if selected_category is None:
            abort(422)

        question = Question(
            question=question_text,
            answer=answer,
            category=category,
            difficulty=difficulty,
        )
        question.insert()

        return jsonify(
            {
                "success": True,
                "created": question.id,
                "total_questions": Question.query.count(),
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        if body is None:
            abort(400)

        search_term = body.get("searchTerm")
        if search_term is None:
            abort(422)

        selection = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).order_by(Question.id)
        questions = [question.format() for question in selection.all()]

        return jsonify(
            {
                "success": True,
                "questions": questions,
                "total_questions": len(questions),
                "current_category": None,
            }
        )

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        category = Category.query.filter(
            Category.id == category_id
        ).one_or_none()

        if category is None:
            abort(404)

        try:
            page = int(request.args.get("page", "1"))
        except (TypeError, ValueError):
            abort(400)

        if page < 1:
            abort(400)

        selection = Question.query.filter(
            Question.category == category_id
        ).order_by(Question.id)
        pagination = selection.paginate(
            page=page,
            per_page=QUESTIONS_PER_PAGE,
            error_out=False,
        )
        questions = [question.format() for question in pagination.items]

        if page > 1 and not questions:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": questions,
                "total_questions": pagination.total,
                "current_category": category.type,
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        body = request.get_json()
        if body is None:
            abort(400)
        if type(body) is not dict:
            abort(400)

        previous_questions = body.get("previous_questions")
        quiz_category = body.get("quiz_category")
        if previous_questions is None or quiz_category is None:
            abort(422)
        if not isinstance(previous_questions, list) or not isinstance(
            quiz_category, dict
        ):
            abort(422)

        category_id = quiz_category.get("id")
        if category_id is None:
            abort(422)

        question_query = Question.query.filter(
            Question.id.notin_(previous_questions)
        )

        if category_id not in (0, "0"):
            if Category.query.filter(
                Category.id == category_id
            ).one_or_none() is None:
                abort(404)
            question_query = question_query.filter(
                Question.category == category_id
            )

        questions = question_query.all()
        question = random.choice(questions).format() if questions else None

        return jsonify({
            "success": True,
            "question": question,
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        print(f"400 error: {error}")
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request: Invalid request parameters",
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        print(f"404 error: {error}")
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found",
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        print(f"422 error: {error}")
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity",
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        print(f"500 error: {error}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": 500,
            "message": "An error has occurred, please try again later",
        }), 500

    return app
