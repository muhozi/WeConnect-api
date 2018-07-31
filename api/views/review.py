"""
    Reviews features Routes
"""
from flask import Blueprint, jsonify, request
from flasgger.utils import swag_from
from sqlalchemy import desc
from api.models.business import Business
from api.models.review import Review
from api.docs.docs import (ADD_BUSINESS_REVIEW_DOCS,
                           BUSINESS_REVIEWS_DOCS)
from api.inputs.inputs import (
    validate, REVIEW_RULES)
from api.helpers import token_id
from api.views import auth

REVIEW = Blueprint('reviews', __name__)


@REVIEW.route('businesses/<business_id>/reviews', methods=['POST'])
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
                status='error', message='Please provide valid details',
                errors=valid)
            response.status_code = 400
            return response
        Review.save({
            'user_id': user_id,
            'description': sent_data['review'],
            'business_id': business.id
        })
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


@REVIEW.route('businesses/<business_id>/reviews', methods=['GET'])
@swag_from(BUSINESS_REVIEWS_DOCS)
def get_business_reviews(business_id):
    """
        Business reviews
    """
    business = Business.get(business_id)
    if business is not None:
        reviews = Review.query.order_by(desc(Review.created_at)).filter_by(
            business_id=Business.get(business_id).id).all()
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
    response.status_code = 404
    return response
