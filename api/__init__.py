"""
     Initialize the app
"""
from flask import Flask, jsonify
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from config import api_config
from flask_cors import CORS
db = SQLAlchemy()

from api.api import API


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
    app.register_blueprint(API)
    CORS(app, resources={r"/api/v1*": {"origins": "*"}})
    app.config.from_object(api_config[config_name])
    db.init_app(app)
    Swagger(app, config=SWAGGER_CONFIG, template=TEMPLATE)
    return app
