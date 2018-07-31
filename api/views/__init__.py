"""
    Our Main api routes
"""
from functools import wraps
from flask import jsonify, request
from api.models.user import User
from api.helpers import token_id
from api.models.token import Token


def auth(arg):
    """ Auth middleware to check logged in user"""
    @wraps(arg)
    def wrap(*args, **kwargs):
        """ Check if token exists in the request header"""
        if request.headers.get('Authorization'):
            token = request.headers.get('Authorization')
            token_exist = Token.query.filter_by(access_token=token).first()
            if token_exist is not None and token_id(token):
                user = User.query.filter_by(id=token_id(token)).first()
                if user.activation_token is not None:
                    response = jsonify({
                        'status': 'error',
                        'message': "Please confirm your email address"
                    })
                    response.status_code = 401
                    return response
                return arg(*args, **kwargs)
        response = jsonify({
            'status': 'error',
            'message': "Unauthorized"
        })
        response.status_code = 401
        return response
    return wrap
