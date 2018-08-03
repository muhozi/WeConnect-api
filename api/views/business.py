"""
    Business features routes
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc
from flasgger.utils import swag_from
from api.models.business import Business
from api.models.review import Review
from api.docs.docs import (REGISTER_BUSINESS_DOCS,
                           GET_ALL_BUSINESSES_DOCS,
                           UPDATE_BUSINESS_DOCS,
                           DELETE_BUSINESS_DOCS,
                           GET_BUSINESS_DOCS)
from api.inputs.inputs import (
    validate,
    REGISTER_BUSINESS_RULES)
from api.helpers import token_id
from api.views import auth

BUSINESS = Blueprint('businesses', __name__)


@BUSINESS.route('', methods=['POST'])
@auth
@swag_from(REGISTER_BUSINESS_DOCS)
def register_business():
    """
        Register business
    """
    sent_data = request.get_json(force=True)
    valid = validate(sent_data, REGISTER_BUSINESS_RULES)
    if valid is not True:
        response = jsonify(
            status='error',
            message="Please provide required info",
            errors=valid)
        response.status_code = 400
        return response
    user_id = token_id(request.headers.get('Authorization'))
    if Business.query.order_by(
            desc(Business.created_at)).filter(
                Business.user_id == user_id, func.lower(
                    Business.name) == func.lower(sent_data['name'])
    ).first() is not None:
        response = jsonify(
            status='error',
            message=("You have already "
                     "registered business with the same name"))
        response.status_code = 400
        return response
    data = {
        'user_id': user_id,
        'name': sent_data['name'],
        'description': sent_data['description'],
        'category': sent_data['category'],
        'country': sent_data['country'],
        'city': sent_data['city']
    }
    Business.save(data)
    response = jsonify({
        'status': 'ok',
        'message': "Your business has been successfully registered"
    })
    response.status_code = 201
    return response


@BUSINESS.route('/<business_id>', methods=['DELETE'])
@auth
@swag_from(DELETE_BUSINESS_DOCS)
def delete_business(business_id):
    """
        Delete business
    """
    user_id = token_id(request.headers.get('Authorization'))
    business = Business.get_by_user(business_id, user_id)
    if business is not None:
        Review.delete_all(business.id)
        business.delete(business.id)
        response = jsonify({
            'status': 'ok',
            'message': "Your business has been successfully deleted"
        })
        response.status_code = 202
        return response
    response = jsonify(
        status='error',
        message="""This business doesn't exist or
          you don't have privileges to it""")
    response.status_code = 400
    return response


@BUSINESS.route('/<business_id>', methods=['PUT'])
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
        if valid is not True:
            response = jsonify(
                status='error',
                message="Please provide required info",
                errors=valid)
            response.status_code = 400
            return response
        data = {
            'name': sent_data['name'],
            'description': sent_data['description'],
            'category': sent_data['category'],
            'country': sent_data['country'],
            'city': sent_data['city'],
        }
        if Business.has_two_same_business(
                user_id, sent_data['name'],
                business_id):
            response = jsonify(
                status='error',
                message=("You have already registered"
                         " a business with same name"))
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
        message=("This business doesn't exist or you"
                 " don't have privileges to it"))
    response.status_code = 400
    return response


@BUSINESS.route('', methods=['GET'])
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
    businesses = Business.query.order_by(
        desc(Business.created_at)).order_by(desc(Business.created_at))

    # Filter by search query
    if query is not None and query.strip() != '':
        businesses = businesses.filter(func.lower(
            Business.name).like('%' + func.lower(query) + '%'))

    # Filter by category
    if category is not None and category.strip() != '':
        businesses = businesses.filter(func.lower(
            Business.category).like('%' + func.lower(category) + '%'))

    # Filter by city
    if city is not None and city.strip() != '':
        businesses = businesses.filter(
            func.lower(Business.city).like('%' + func.lower(city) + '%'))

    # Filter by country
    if country is not None and country.strip() != '':
        businesses = businesses.filter(func.lower(
            Business.country).like('%' + func.lower(country) + '%'))

    errors = []  # Errors list

    if (per_page is not None and per_page.isdigit() is False and
            per_page.strip() != ''):
        errors.append({'limit': 'Invalid limit page limit number'})

    if page is not None and page.isdigit() is False and page.strip() != '':
        errors.append({'page': 'Invalid page number'})

    if len(errors) is not 0:
        response = jsonify(
            status='error',
            message="Please provide valid details",
            errors=errors)
        response.status_code = 400
        return response

    page = int(page) if page is not None and page.strip() != '' else 1
    per_page = int(
        per_page) if per_page is not None and per_page.strip() != '' else 20

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


@BUSINESS.route('/<business_id>', methods=['GET'])
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
