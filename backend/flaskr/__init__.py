import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from config import config
from models import db, Question, Category
from flask_migrate import Migrate
import sys

QUESTIONS_PER_PAGE = 10
migrate = Migrate()


def paginate_questions(request, collections):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [q.format() for q in collections]
    current_questions = questions[start:end]
    return current_questions


def create_app(config_file='development'):
    # create and configure the app
    app = Flask(__name__)
    app.app_context().push()
    app.config.from_object(config[config_file])
    config[config_file].init_app(app)
    app.config.from_pyfile("../config.py")
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # GET categories
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        # convert categories into a dictionary
        category_dict = {}
        for category in categories:
            category_dict[category.id] = category.type

        return jsonify({
            "success": True,
            "categories": category_dict,
            "total_categories": len(categories),
        })

    # GET questions
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()

        if len(current_questions) == 0:
            abort(404)

        # convert categories into a dictionary
        category_dict = {}
        for category in categories:
            category_dict[category.id] = category.type

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': None,
            'categories': category_dict
        })

    # DELETE a specific question
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # look for the question by the question_id
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        # If the quesion does not exist, abort with 404
        if question is None:
            abort(404)
        try:
            question.delete()

            # After deleting the question, generate the paginated questions
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'deleted': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except BaseException:
            print(sys.exc_info())
            abort(422)

    # POST a question
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        # If any field is missed, abort with 400.
        if (not new_question) or (not new_answer) or (
                not new_category) or (not new_difficulty):
            abort(400)
        try:
            # question constructor
            question = Question(
                new_question,
                new_answer,
                new_category,
                new_difficulty)
            question.insert()

            # After inserting the question, generate the paginated questions
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except BaseException:
            print(sys.exc_info())
            abort(422)

    # POST a question search
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        # If there is no search term, abort with 400.
        if search_term is None:
            abort(400)
        try:
            # Generate the paginated questions whose substring matches the
            # search term
            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': None
            })
        except BaseException:
            print(sys.exc_info())
            abort(422)

    # GET questions from a category
    @app.route('/categories/<int:category_id>/questions')
    def get_specific_questions(category_id):
        # if Category.query.get(category_id) is None:
        if db.session.get(Category, category_id) is None:
            abort(404)
        try:
            # generate the paginated questions whose catetories equal to
            # category_id
            selection = Question.query.filter(
                Question.category == category_id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': category_id
            })
        except BaseException:
            print(sys.exc_info())
            abort(422)

    # POST quizzes
    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():
        body = request.get_json()
        category = body.get('quiz_category', None)
        previous = body.get('previous_questions', None)

        # If missing quiz_category or previous_questions, abort with 400.
        if (category is None) or (previous is None):
            abort(400)
        try:
            # If category belongs to All, filter questions whose id is not in
            # the previous_questions
            if category['id'] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous)).all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous)).filter(
                    Question.category == category['id']).all()

            # if no more new questions, the next_question is none
            if len(questions) == 0:
                next_question = None
            # else, pick the next_question from the questions randomly
            else:
                next_question = questions[random.randrange(
                    0, len(questions))].format()
            return jsonify({
                'success': True,
                'question': next_question
            })
        except BaseException:
            print(sys.exc_info())
            abort(422)

    # POST a category
    @app.route('/categories', methods=['POST'])
    def create_category():
        body = request.get_json()
        category_type = body.get('type', None)

        # If there is no category type, abort with 400.
        if category_type is None:
            abort(400)
        try:
            # Category constructor
            category = Category(category_type)
            category.insert()

            # convert the categories into a dictionary
            categories = Category.query.order_by(Category.id).all()
            category_dict = {}
            for category in categories:
                category_dict[category.id] = category.type

            return jsonify({
                'success': True,
                'created': category.id,
                'categories': category_dict,
                'total_categories': len(categories)
            })
        except BaseException:
            print(sys.exc_info())
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "Unprocessable Entity"
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "Method Not Allowed"
        }), 405

    return app
