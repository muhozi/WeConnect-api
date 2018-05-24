"""
    Main test
"""
from flask import json
from tests.test_api import MainTests
from api.models.review import Review
from api.models import db


class ReviewTests(MainTests):
    """
        Review tests
    """
    def test_add_business_review(self):
        '''
            Test adding business review
        '''
        self.add_business()
        response = self.app.post(self.url_prefix + 'businesses/' +
                                 self.business_data['hashid'] + '/reviews',
                                 data=json.dumps({
                                     'review': 'We enjoy your coffee',
                                 }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            b'Your review has been sent', response.data)

    def test_add_invalid_business_rev(self):
        '''
            Test adding review to business which doesn't exist
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
            Test adding empty review
        '''
        self.add_business()
        response = self.app.post(self.url_prefix + 'businesses/' +
                                 self.business_data['hashid'] + '/reviews',
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
        review = Review(
            user_id=self.sample_user['id'],
            business_id=self.business_data['id'],
            description="Awesome! We love it",
        )
        db.session.add(review)
        db.session.commit()
        review2 = Review(
            user_id=self.sample_user['id'],
            business_id=self.business_data['id'],
            description="I can't wait to come back",
        )
        db.session.add(review2)
        db.session.commit()
        response = self.app.get(
            self.url_prefix + 'businesses/' + self.business_data['hashid'] + '/reviews')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'reviews', response.data)

    def test_add_rev_invalid_business(self):
        '''
            Test adding a review to non-exist business 
        '''
        response = self.app.post(self.url_prefix + 'businesses/hdfbsjd/reviews',
                                 data=json.dumps({
                                     'review': 'We enjoy your coffee',
                                 }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'business doesn\'t exist', response.data)
