"""
    User features routes
"""
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger.utils import swag_from
from sqlalchemy import func, desc
from api.models.user import User
from api.models.business import Business
from api.models.token import Token
from api.models.password_reset import PasswordReset
from api.docs.docs import (REGISTER_DOCS,
                           LOGIN_DOCS,
                           LOGOUT_DOCS,
                           CONFIRM_EMAIL_DOCS,
                           RESET_LINK_DOCS,
                           RESET_PASSWORD_DOCS,
                           CHANGE_PASSWORD_DOCS,
                           GET_BUSINESSES_DOCS)
from api.inputs.inputs import (
    validate, REGISTER_RULES, LOGIN_RULES, RESET_PWD_RULES,
    CHANGE_PWD_RULES, RESET_LINK_RULES, CONFIRM_EMAIL_RULES)
from api.helpers import (get_token, token_id, generate_reset_token,
                         get_confirm_email_token, send_mail)
from api.views import auth

USER = Blueprint('users', __name__)


@USER.route('auth/register', methods=['POST'])
@swag_from(REGISTER_DOCS)
def register():
    """
        User Registration
    """
    valid = validate(request.get_json(force=True), REGISTER_RULES)
    sent_data = request.get_json(force=True)
    if valid is not True:
        response = jsonify(
            status='error',
            message="Please provide valid details",
            errors=valid)
        response.status_code = 400
        return response
    logged_user = User.get_user(sent_data['email'])
    if logged_user is None:
        user = User.query.filter_by(username=sent_data['username']).first()
        if user is not None:
            response = jsonify({
                'status': 'error',
                'errors': [{
                    'username': 'Username was taken',
                }],
                'message': "Please provide valid details"
            })
            response.status_code = 400
            return response
        gen_token = get_confirm_email_token()
        User.save({
            'username': sent_data['username'],
            'email': sent_data['email'],
            'activation_token': gen_token,
            'password': generate_password_hash(sent_data['password'])
        })
        origin_url = request.headers.get('Origin') or ''
        confirm_link = '{}/auth/confirm-password/{}'.format(
            origin_url, gen_token)
        email = ''.join(
                ('<h2>Hello {} , </h2><br>To ',
                 'Click <b><a href={}>Here</a></b> to confirm your email'
                 )).format(sent_data['username'],
                           confirm_link)
        send_mail(sent_data['email'], email)
        response = jsonify({
            'status': 'ok',
            'message': """You have been successfully registered,
                        Please confirm email address"""
        })
        response.status_code = 201
        return response
    if logged_user.activation_token is not None:
        gen_token = get_confirm_email_token()
        User.update_token(logged_user.id, gen_token)
        origin_url = request.headers.get('Origin') or ''
        confirm_link = '{}/auth/confirm-password/{}'.format(
            origin_url, gen_token)
        email = ''.join(
                ('<h2>Hello {} , </h2><br>To ',
                 'Click <b><a href={}>Here</a></b> to confirm your email'
                 )).format(logged_user.username,
                           confirm_link)
        send_mail(sent_data['email'], email)
        response = jsonify({
            'status': 'ok',
            'message': """
                        You have been successfully registered,
                        Please confirm email address used"""
        })
        response.status_code = 201
        return response
    else:
        errors = {}
        if logged_user.username == sent_data['username']:
            errors['username'] = ['Username has been taken']
        if logged_user.email == sent_data['email']:
            errors['email'] = ['Email has been taken']
        response = jsonify({
            'status': 'error',
            'errors': errors,
            'message': "Please provide valid details"
        })
        response.status_code = 400
        return response


@USER.route('auth/logout', methods=['POST'])
@auth
@swag_from(LOGOUT_DOCS)
def logout():
    """
        User logout
    """
    token = Token.query.filter_by(
        access_token=request.headers.get('Authorization')).first()
    Token.delete(token.id)
    response = jsonify({
        'status': 'ok',
        'message': "You have successfully logged out"
    })
    response.status_code = 200
    return response


@USER.route('auth/login', methods=['POST'])
@swag_from(LOGIN_DOCS)
def login():
    """
        User login
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, LOGIN_RULES)
    if valid is not True:
        response = jsonify(
            status='error',
            message="Please provide valid details",
            errors=valid)
        response.status_code = 400
        return response
    data = {
        'email': sent_data['email'],
        'password': sent_data['password'],
    }
    # Check if email exists
    logged_user = User.get_user(data['email'])
    if logged_user is not None:
        # Check password
        if check_password_hash(logged_user.password, data['password']):
            if logged_user.activation_token is not None:
                response = jsonify({
                    'status': 'error',
                    'message': "Please confirm your email address"
                })
                response.status_code = 401
                return response
            token_ = get_token(logged_user.id)
            Token.save({
                'user_id': logged_user.id,
                'access_token': token_,
            })
            response = jsonify({
                'status': 'ok',
                'message': 'You have been successfully logged in',
                'access_token': token_,
                'user': {
                    'username': logged_user.username,
                    'email': logged_user.email
                }
            })
            response.status_code = 200
            # response.headers['auth_token'] = token
            return response
    response = jsonify({
        'status': 'error',
        'message': "Invalid email or password"
    })
    response.status_code = 401
    return response


@USER.route('auth/change-password', methods=['POST'])
@auth
@swag_from(CHANGE_PASSWORD_DOCS)
def change_password():
    """
        Change password
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, CHANGE_PWD_RULES)
    if valid is not True:
        response = jsonify(status='error',
                           message="Please provide valid details",
                           errors=valid)
        response.status_code = 400
        return response
    user_id = token_id(request.headers.get('Authorization'))
    user = User.query.filter_by(id=user_id).first()
    if check_password_hash(user.password, sent_data['old_password']) is False:
        response = jsonify({
            'status': 'error',
            'message': "Invalid old password"
        })
        response.status_code = 400
        return response
    User.update_password(
        user.id, generate_password_hash(sent_data['new_password']))
    response = jsonify({
        'status': 'ok',
        'message': "You have successfully changed your password"
    })
    response.status_code = 201
    return response


@USER.route('auth/reset-password/<token>', methods=['POST'])
@swag_from(RESET_PASSWORD_DOCS)
def reset_password(token):
    """
        Reset password reset
    """
    sent_data = request.get_json(force=True)
    print(sent_data)
    valid = validate(sent_data, RESET_PWD_RULES)
    if valid is not True:
        response = jsonify(status='error',
                           message="Please provide valid details",
                           errors=valid)
        response.status_code = 400
        return response
    token = PasswordReset.query.filter_by(reset_token=token).first()
    if token is None:
        response = jsonify({
            'status': 'error',
            'message': "Invalid reset token"
        })
        response.status_code = 400
        return response
    user = User.query.filter_by(id=token.user_id).first()
    User.update_password(
        user.id, generate_password_hash(sent_data['password']))
    PasswordReset.delete(token.id)
    response = jsonify({
        'status': 'ok',
        'message': "You have successfully reset your password"
    })
    response.status_code = 201
    return response


@USER.route('auth/confirm/<token>', methods=['POST'])
@swag_from(CONFIRM_EMAIL_DOCS)
def confirm_email(token):
    """
        Confirm email address
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, CONFIRM_EMAIL_RULES)
    if valid is not True:
        response = jsonify(status='error',
                           message="Please provide valid details",
                           errors=valid)
        response.status_code = 400
        return response
    token = User.query.filter_by(
        activation_token=token, email=sent_data['email']).first()
    if token is None:
        response = jsonify({
            'status': 'error',
            'message': "Invalid reset token or email"
        })
        response.status_code = 400
        return response
    user = User.query.filter_by(id=token.id, email=sent_data['email']).first()
    if user is not None:
        User.activate(user.id)
        response = jsonify({
            'status': 'ok',
            'message': "Your email was confirmed"
        })
        response.status_code = 200
        return response
    response = jsonify({
        'status': 'ok',
        'message': "Invalid confirm token token or email"
    })
    response.status_code = 400
    return response


@USER.route('auth/reset-password', methods=['POST'])
@swag_from(RESET_LINK_DOCS)
def reset_link():
    """
        Reset link
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, RESET_LINK_RULES)
    if valid is not True:
        response = jsonify(status='error',
                           message="Please provide valid details",
                           errors=valid)
        response.status_code = 400
        return response
    user = User.query.filter_by(email=sent_data['email']).first()
    if user is None:
        response = jsonify({
            'status': 'error',
            'message': "Email doesn't exist"
        })
        response.status_code = 400
        return response
    PasswordReset.query.filter_by(user_id=user.id).delete()
    gen_token = generate_reset_token()
    PasswordReset.save(user.id, gen_token)
    origin_url = request.headers.get('Origin') or ''
    reset_link = '{}/auth/reset-password/{}'.format(origin_url, gen_token)
    email = ''.join(
            ('<h2>Hello {} , </h2><br>To ',
             'reset your password click <b><a href={}>Here</a></b>'
             )).format(user.username,
                       reset_link)
    send_mail(
        user.email, email)
    response = jsonify({
        'status': 'ok',
        'message': "Check your email to reset password"
    })
    response.status_code = 201
    return response


@USER.route('account/businesses', methods=['GET'])
@auth
@swag_from(GET_BUSINESSES_DOCS)
def get_user_businesses():
    """
        User's Businesses list
    """
    user_id = token_id(request.headers.get('Authorization'))
    query = request.args.get('q')
    category = request.args.get('category')
    city = request.args.get('city')
    country = request.args.get('country')
    page = request.args.get('page')
    per_page = request.args.get('limit')
    businesses = Business.query.order_by(
        desc(Business.created_at)).filter_by(user_id=user_id)
    if businesses.count() is not 0:

        # Filter by search query
        if query is not None and query.strip() != '':
            businesses = businesses.filter(func.lower(
                Business.name).like('%' + func.lower(query) + '%'))

        # Filter by category
        if category is not None and category.strip() != '':
            businesses = businesses.filter(func.lower(
                Business.category) == func.lower(category))

        # Filter by city
        if city is not None and city.strip() != '':
            businesses = businesses.filter(
                func.lower(Business.city) == func.lower(city))

        # Filter by country
        if country is not None and country.strip() != '':
            businesses = businesses.filter(func.lower(
                Business.country) == func.lower(country))

        errors = []  # Errors list

        if (per_page is not None and per_page.isdigit() is False and
                per_page.strip() != ''):
            errors.append({'limit': 'Invalid limit page limit number'})

        if page is not None and page.isdigit() is False and page.strip() != '':
            errors.append({'page': 'Invalid page number'})

        if len(errors) is not 0:
            response = jsonify(
                status='error', message="Please provide valid details",
                errors=errors)
            response.status_code = 400
            return response

        page = int(page) if page is not None and page.strip() != '' else 1
        per_page = int(
            per_page) if ((per_page is not None)
                          and (per_page.strip() != '')) else 20

        # Overall filter results
        businesses = businesses.paginate(per_page=per_page, page=page)

        if len(Business.serializer(businesses.items)) is not 0:
            response = jsonify({
                'status': 'ok',
                'message': 'There are {} businesses found'.format(
                    str(len(businesses.items))
                ),
                'next_page': businesses.next_num,
                'previous_page': businesses.prev_num,
                'current_page': businesses.page,
                'pages': businesses.pages,
                'total_businesses': businesses.total,
                'businesses': Business.serializer(businesses.items)
            })
            response.status_code = 200
            return response
        response = jsonify(
            status='error', message="No business found!")
        response.status_code = 200
        return response

    response = jsonify(
        status='error', message="You don't have any registered business")
    response.status_code = 200
    return response
