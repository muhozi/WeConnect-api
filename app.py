"""
    Main file to run the app
"""
import os
from flask import jsonify, redirect
from api.index import create_app
from api.models import db
from flask_migrate import Migrate
from flask_mail import Mail
# Init Flask mail
mail = Mail()
APP = create_app(os.getenv('ENV'))
migrate = Migrate(APP, db)


@APP.errorhandler(404)
def not_found(error):
    """
        Return json error if page not found
    """
    return jsonify({
        'status': 'error',
        'message': 'Page not found'
    }), 404


@APP.errorhandler(400)
def bad_request(e):
    """
        Bad request json response
    """
    return jsonify({
        'status': 'error',
        'message': 'Bad request'
    }), 400


@APP.errorhandler(500)
def internal_server_error(e):
    """
        Bad request json response
    """
    return jsonify({
        'status': 'error',
        'message': 'Something went wrong at our end'
    }), 500


@APP.route('/')
def api_docs_redirect():
    """ Redirect to API docs """
    return redirect('/api/v1', code=302)


if __name__ == '__main__':
    # Run the application
    APP.run()
