"""
    Main file to run the app
"""
import os
from flask import jsonify, redirect
from api import create_app
from api.models import db
from flask_migrate import Migrate
APP = create_app(os.getenv('ENV'))
migrate = Migrate(APP, db)


@APP.errorhandler(404)
def page_not_found(e):
    """
        Return json error if page not found
    """
    return jsonify({
        'status': 'error',
        'message': 'Page not found'
    }), 404


@APP.route('/')
def helapi_docslo():
    return redirect('/api/v1', code=302)

if __name__ == '__main__':
    # Run the application
    APP.run()
