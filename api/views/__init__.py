"""
    Our Main api routes
"""
from functools import wraps
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flasgger.utils import swag_from
from api.models.user import User
from api.models.business import Business
from api.models.review import Review
from api.models.token import Token
from api.models.password_reset import PasswordReset
from api.docs.docs import (REGISTER_DOCS,
                           LOGIN_DOCS,
                           LOGOUT_DOCS,
                           RESET_LINK_DOCS,
                           RESET_PASSWORD_DOCS,
                           CHANGE_PASSWORD_DOCS,
                           REGISTER_BUSINESS_DOCS,
                           GET_BUSINESSES_DOCS,
                           GET_ALL_BUSINESSES_DOCS,
                           UPDATE_BUSINESS_DOCS,
                           DELETE_BUSINESS_DOCS,
                           BUSINESS_REVIEWS_DOCS,
                           ADD_BUSINESS_REVIEW_DOCS,
                           GET_BUSINESS_DOCS)
from api.inputs.inputs import (
    validate, REGISTER_RULES, LOGIN_RULES, RESET_PWD_RULES,
    CHANGE_PWD_RULES, RESET_LINK_RULES,
    REGISTER_BUSINESS_RULES, REVIEW_RULES)
from api.helpers import get_token, token_id, generate_reset_token, send_mail

def auth(arg):
    """ Auth middleware to check logged in user"""
    @wraps(arg)
    def wrap(*args, **kwargs):
        """ Check if token exists in the request header"""
        if request.headers.get('Authorization'):
            token = request.headers.get('Authorization')
            token_exist = Token.query.filter_by(access_token=token).first()
            if token_exist is not None and token_id(token):
                return arg(*args, **kwargs)
        response = jsonify({
            'status': 'error',
            'message': "Unauthorized"
        })
        response.status_code = 401
        return response
    return wrap
