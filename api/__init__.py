"""
     Initialize the app
"""
from flask import Flask, jsonify
from flasgger import Swagger
from dotenv import load_dotenv
from flask_cors import CORS
from flask_mail import Mail
from config import api_config
from api.models import db
# Init Flask mail
mail = Mail()
from api.views.user import USER
from api.views.business import BUSINESS
from api.views.review import REVIEW
# from api.api import API

# Swagger configurations
SWAGGER_CONFIG = {
    "headers": [],
    "title": "WeConnect",
    "specs": [
        {
            "version": "1",
            "title": "Api v1",
            "endpoint": 'apispec',
            "route": '/api/v1/docs.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/swagger_files",
    "swagger_ui": True,
    "specs_route": "/api/v1"
}
TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "WeConnect",
        "description": "WeConnect Platform API v1",
        "version": "1"
    },
    "consumes": [
        "application/json",
    ],
    "produces": [
        "application/json",
    ],
    "schemes": [
        "http",
        "https"
    ],
    "operationId": "getmyData"
}


def create_app(config_name):
    """
        App init function
    """
    app = Flask(__name__, instance_relative_config=True)
    # Register blueprint
    prefix = '/api/v1/'
    # Register blueprints
    app.register_blueprint(USER, url_prefix=prefix)
    app.register_blueprint(BUSINESS, url_prefix=prefix+'businesses')
    app.register_blueprint(REVIEW, url_prefix=prefix)
    CORS(app, resources={r"/api/v1*": {"origins": "*"}})
    app.config.from_object(api_config[config_name])
    mail.init_app(app)
    db.init_app(app)
    Swagger(app, config=SWAGGER_CONFIG, template=TEMPLATE)
    return app
