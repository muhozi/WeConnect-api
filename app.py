"""
    Main file to run the app
"""
import os
from flask import jsonify
from api import create_app
from flask_migrate import Migrate
from api.models import db
APP = create_app(os.getenv('ENV'))
migrate = Migrate(APP, db)


# @APP.errorhandler(404)
# def page_not_found():
#     """
#         Return json error if page not found
#     """
#     return jsonify({
#         'status': 'error',
#         'message': 'Page not found'
#     }), 404


if __name__ == '__main__':
    # Run the application
    APP.run()
