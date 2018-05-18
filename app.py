"""
    Main file to run the app
"""
import os
from flask import jsonify
from api.api import User, Business, Review
from api import create_app, db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
APP = create_app(os.getenv('ENV'))
migrate = Migrate(APP, db)


@APP.errorhandler(404)
def page_not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'Page not found'
    }), 404


if __name__ == '__main__':
    # Run the application
    APP.run()
