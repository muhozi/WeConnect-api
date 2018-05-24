"""
    Our Main api routes
"""
import ssl
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
from api import db

API = Blueprint('v1', __name__, url_prefix='/api/v1')
# Monkey patch SSL Error
ssl._create_default_https_context = ssl._create_unverified_context

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


@API.route('/auth/register', methods=['POST'])
@swag_from(REGISTER_DOCS)
def register():
    """
        User Registration
    """
    valid = validate(request.get_json(force=True), REGISTER_RULES)
    sent_data = request.get_json(force=True)
    if valid != True:
        response = jsonify(
            status='error', message="Please provide valid details", errors=valid)
        response.status_code = 400
        return response
    user = User(
        username=sent_data['username'],
        email=sent_data['email'],
        password=generate_password_hash(sent_data['password'])
    )
    db.session.add(user)
    db.session.commit()
    response = jsonify({
        'status': 'ok',
        'message': "You have been successfully registered"
    })
    response.status_code = 201
    return response


@API.route('/auth/logout', methods=['POST'])
@auth
@swag_from(LOGOUT_DOCS)
def logout():
    """
        User logout
    """
    token = Token.query.filter_by(
        access_token=request.headers.get('Authorization')).first()
    db.session.delete(token)
    db.session.commit()
    response = jsonify({
        'status': 'ok',
        'message': "You have successfully logged out"
    })
    response.status_code = 200
    return response


@API.route('/auth/login', methods=['POST'])
@swag_from(LOGIN_DOCS)
def login():
    """
        User login
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, LOGIN_RULES)
    if valid != True:
        response = jsonify(
            status='error', message="Please provide valid details", errors=valid)
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
            token_ = get_token(logged_user.id)
            token = Token(
                user_id=logged_user.id,
                access_token=token_,
            )
            db.session.add(token)
            db.session.commit()
            response = jsonify({
                'status': 'ok',
                'message': 'You have been successfully logged in',
                'access_token': token.access_token,
            })
            response.status_code = 200
            # response.headers['auth_token'] = token
            return response
        response = jsonify({
            'status': 'error',
            'message': "Invalid password"
        })
        response.status_code = 401
        return response
    response = jsonify({
        'status': 'error',
        'message': "Invalid email or password"
    })
    response.status_code = 401
    return response


@API.route('/auth/change-password', methods=['POST'])
@auth
@swag_from(CHANGE_PASSWORD_DOCS)
def change_password():
    """
        Change password
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, CHANGE_PWD_RULES)
    if valid != True:
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
    user.password = generate_password_hash(sent_data['new_password'])
    db.session.add(user)
    db.session.commit()
    response = jsonify({
        'status': 'ok',
        'message': "You have successfully changed your password"
    })
    response.status_code = 201
    return response

@API.route('/auth/reset-password/<token>', methods=['POST'])
@swag_from(RESET_PASSWORD_DOCS)
def reset_password(token):
    """
        Reset password reset
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, RESET_PWD_RULES)
    if valid != True:
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
    user.password = generate_password_hash(sent_data['password'])
    db.session.add(user)
    db.session.commit()
    db.session.delete(token)
    db.session.commit()
    response = jsonify({
        'status': 'ok',
        'message': "You have successfully reset your password"
    })
    response.status_code = 201
    return response

@API.route('/auth/reset-password', methods=['POST'])
@swag_from(RESET_LINK_DOCS)
def reset_link():
    """
        Reset link
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, RESET_LINK_RULES)
    if valid != True:
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
    reset_token =  PasswordReset(user_id=user.id,reset_token=gen_token)
    db.session.add(reset_token)
    db.session.commit()
    print("OK Email is running *********************************")
    send_mail(user.email, '<h2>Hello ' + user.username +
              ', </h2><br>You password reset token is: <b>'+gen_token+'</b>')
    response = jsonify({
        'status': 'ok',
        'message': "Check your email to reset password"
    })
    response.status_code = 201
    return response

@API.route('/businesses', methods=['POST'])
@auth
@swag_from(REGISTER_BUSINESS_DOCS)
def register_business():
    """
        Register business
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, REGISTER_BUSINESS_RULES)
    if valid != True:
        response = jsonify(
            status='error', message="Please provide required info", errors=valid)
        response.status_code = 400
        return response
    user_id = token_id(request.headers.get('Authorization'))
    if Business.query.filter_by(user_id=user_id, name=sent_data['name']).first() is not None:
        response = jsonify(
            status='error', message="You have already a registered business with the same name")
        response.status_code = 400
        return response
    business = Business(
        user_id=user_id,
        name=sent_data['name'],
        description=sent_data['description'],
        category=sent_data['category'],
        country=sent_data['country'],
        city=sent_data['city']
    )
    db.session.add(business)
    db.session.commit()
    response = jsonify({
        'status': 'ok',
        'message': "Your business has been successfully registered"
    })
    response.status_code = 201
    return response


@API.route('/businesses/<business_id>', methods=['DELETE'])
@auth
@swag_from(DELETE_BUSINESS_DOCS)
def delete_business(business_id):
    """
        Delete business
    """
    user_id = token_id(request.headers.get('Authorization'))
    business = Business.get_by_user(business_id, user_id)
    if business is not None:
        db.session.delete(business)
        db.session.commit()
        response = jsonify({
            'status': 'ok',
            'message': "Your business has been successfully deleted"
        })
        response.status_code = 202
        return response
    response = jsonify(
        status='error',
        message="This business doesn't exist or you don't have privileges to it")
    response.status_code = 400
    return response


@API.route('/businesses/<business_id>', methods=['PUT'])
@auth
@swag_from(UPDATE_BUSINESS_DOCS)
def update_business(business_id):
    """
        Update business
    """
    sent_data = request.get_json(force=True)
    user_id = token_id(request.headers.get('Authorization'))
    business = Business.get_by_user(business_id, user_id)
    if business is not None:
        valid = validate(sent_data, REGISTER_BUSINESS_RULES)
        if valid != True:
            response = jsonify(
                status='error', message="Please provide required info", errors=valid)
            response.status_code = 400
            return response
        data = {
            'name': sent_data['name'],
            'description': sent_data['description'],
            'category': sent_data['category'],
            'country': sent_data['country'],
            'city': sent_data['city'],
        }
        if Business.has_two_same_business(user_id, sent_data['name'], business_id):
            response = jsonify(
                status='error',
                message="You have already registered a business with same name")
            response.status_code = 400
            return response
        Business.update(business_id, data)
        response = jsonify({
            'status': 'ok',
            'message': "Your business has been successfully updated"
        })
        response.status_code = 202
        return response
    response = jsonify(
        status='error',
        message="This business doesn't exist or you don't have privileges to it")
    response.status_code = 400
    return response


@API.route('/account/businesses', methods=['GET'])
@auth
@swag_from(GET_BUSINESSES_DOCS)
def get_user_businesses():
    """
        User's Businesses list
    """
    user_id = token_id(request.headers.get('Authorization'))
    businesses = Business.user_businesses(user_id)
    if len(businesses) is not 0:
        response = jsonify({
            'status': 'ok',
            'message': 'You have businesses ' + str(len(businesses)) + ' registered businesses',
            'businesses': Business.serializer(businesses)
        })
        response.status_code = 200
        return response
    response = jsonify(
        status='error', message="You don't have registered any business")
    response.status_code = 200
    return response


@API.route('/businesses', methods=['GET'])
@swag_from(GET_ALL_BUSINESSES_DOCS)
def get_all_businesses():
    """
        Get all Businesses
    """
    query = request.args.get('q')
    category = request.args.get('category')
    city = request.args.get('city')
    country = request.args.get('country')
    page = request.args.get('page')
    per_page = request.args.get('limit')
    businesses = Business.query

    # Filter by search query
    if query is not None and query.strip() != '':
        businesses = businesses.filter(func.lower(Business.name).like('%'+ func.lower(query) +'%'))

    # Filter by category
    if category is not None and category.strip() != '':
        businesses = businesses.filter(func.lower(Business.category) == func.lower(category))

    # Filter by city
    if city is not None and city.strip() != '':
        businesses = businesses.filter(func.lower(Business.city) == func.lower(city))

    # Filter by country
    if country is not None and country.strip() != '':
        businesses = businesses.filter(func.lower(Business.country) == func.lower(country))

    errors = [] # Errors list

    if per_page is not None and per_page.isdigit() is False and per_page.strip() != '':
        errors.append({'limit':'Invalid limit page limit number'})

    if page is not None and page.isdigit() is False and page.strip() != '':
        errors.append({'page':'Invalid page number'})

    if len(errors) is not 0:
        response = jsonify(
            status='error', message="Please provide valid details", errors=errors)
        response.status_code = 400
        return response

    page = int(page) if page is not None and page.strip() != '' else 1
    per_page = int(per_page) if per_page is not None and per_page.strip() != '' else 20

    # Overall filter results
    businesses = businesses.paginate(per_page=per_page, page=page)

    if len(Business.serializer(businesses.items)) is not 0:
        response = jsonify({
            'status': 'ok',
            'message': 'There are ' + str(len(businesses.items)) + ' businesses found',
            'next_page': businesses.next_num,
            'previous_page': businesses.prev_num,
            'total_businesses': businesses.total,
            'businesses': Business.serializer(businesses.items)
        })
        response.status_code = 200
        return response
    response = jsonify(
        status='error', message="No business found!")
    response.status_code = 200
    return response


@API.route('/businesses/<business_id>', methods=['GET'])
@swag_from(GET_BUSINESS_DOCS)
def get_business(business_id):
    """
        Get business
    """
    business = Business.get(business_id)
    if business is not None:
        response = jsonify({
            'status': 'ok',
            'message': 'Business found',
            'business': Business.serialize_obj(business),
        })
        response.status_code = 200
        return response
    response = jsonify({
        'status': 'error',
        'message': "Business not found"
    })
    response.status_code = 400
    return response


@API.route('/businesses/<business_id>/reviews', methods=['POST'])
@auth
@swag_from(ADD_BUSINESS_REVIEW_DOCS)
def add_business_review(business_id):
    """
        Add Review
    """
    user_id = token_id(request.headers.get('Authorization'))
    business = Business.get(business_id)
    if business is not None:
        sent_data = request.get_json(force=True)
        valid = validate(sent_data, REVIEW_RULES)
        if valid is not True:
            response = jsonify(
                status='error', message='Please provide valid details', errors=valid)
            response.status_code = 400
            return response
        review = Review(
            user_id=user_id,
            description=sent_data['review'],
            business_id=business.id
        )
        db.session.add(review)
        db.session.commit()
        response = jsonify({
            'status': 'ok',
            'message': "Your review has been sent"
        })
        response.status_code = 201
        return response
    response = jsonify({
        'status': 'error',
        'message': "This business doesn't exist"
    })
    response.status_code = 400
    return response


@API.route('/businesses/<business_id>/reviews', methods=['GET'])
@swag_from(BUSINESS_REVIEWS_DOCS)
def get_business_reviews(business_id):
    """
        Business reviews
    """
    business = Business.get(business_id)
    if business is not None:
        reviews = Review.query.filter_by(business_id=Business.get(business_id).id).all()
        if len(reviews) is not 0:
            response = jsonify({
                'status': 'ok',
                'message': str(len(reviews)) + " reviews found",
                'business': Business.serialize_obj(business),
                'reviews': Review.serializer(reviews)
            })
            response.status_code = 200
            return response
        response = jsonify({
            'status': 'ok',
            'message': "No business review yet",
            'business': Business.serialize_obj(business),
            'reviews': []
        })
        response.status_code = 200
        return response
    response = jsonify({
        'status': 'error',
        'message': "This business doesn't exist"
    })
    response.status_code = 400
    return response
