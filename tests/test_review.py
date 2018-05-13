"""
    Main test
"""
import datetime
import uuid
from flask import json
from api.models.user import User
from api.models.business import Business
from api.models.review import Review
from api.helpers import get_token
from tests.test_api import MainTests


class ReviewTests(MainTests):
    """
        Review tests
    """
    # def __init__(self,arg):
    #     self.add_business()

    def test_add_business_review(self):
        '''
            Test adding business review
        '''
        self.add_business()
        response = self.app.post(self.url_prefix + 'businesses/' + self.business_data['hashid'] + '/reviews',
                                 data=json.dumps({
                                     'review': 'We enjoy your coffee',
                                 }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            b'Your review has been sent', response.data)

    def test_add_review_to_invalid_business(self):
        '''
            Test adding business review to business which doesn't exist
        '''
        response = self.app.post(self.url_prefix + 'businesses/hdfbsjd/reviews',
                                 data=json.dumps({
                                     'review': 'We enjoy your coffee',
                                 }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'business doesn\'t exist', response.data)

    def test_adding_empty_review(self):
        '''
            Test adding business review to business which doesn't exist
        '''
        self.add_business()
        response = self.app.post(self.url_prefix + 'businesses/' + self.business_data['hashid'] + '/reviews',
                                 data=json.dumps({
                                     'review': '',
                                 }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'provide valid details', response.data)

    def test_no_business_reviews(self):
        '''
            Test retrieving business reviews with no reviews
        '''
        self.add_business()
        response = self.app.get(
            self.url_prefix + 'businesses/' + self.business_data['hashid'] + '/reviews')
        self.assertIn(
            b'No business review yet', response.data)

    def test_no_exist_business_reviews(self):
        '''
            Test retrieving reviews business which doesn't exist
        '''
        response = self.app.get(
            self.url_prefix + 'businesses/any_dummy_id/reviews')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'This business doesn\'t exist', response.data)

    def test_business_reviews(self):
        '''
            Test retrieving business reviews
        '''
        self.add_business()
        response = self.app.get(
            self.url_prefix + 'businesses/' + self.business_data['hashid'] + '/reviews')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'reviews', response.data)

    def test_add_review_to_invalid_business(self):
        '''
            Test adding business review to business which doesn't exist
        '''
        response = self.app.post(self.url_prefix + 'businesses/hdfbsjd/reviews',
                                 data=json.dumps({
                                     'review': 'We enjoy your coffee',
                                 }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'business doesn\'t exist', response.data)

