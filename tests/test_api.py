"""
    Main tests
"""
import unittest
from werkzeug.security import generate_password_hash
from api import create_app
from api.models.user import User
from api.models.token import Token
from api.models.business import Business
from api.helpers import get_token
from api import db


class MainTests(unittest.TestCase):
    """
        Main tests class
    """
    url_prefix = '/api/v1/'

    def setUp(self):
        """
            Set up test data
        """
        # db.init_app(APP)
        self.main = create_app('testing')
        self.app = self.main.test_client()
        self.app_context = self.main.app_context()
        self.app_context.push()
        with self.app_context:
            db.init_app(self.main)
            db.create_all()
        self.sample_user = {
            'username': 'Muhozi',
            'email': 'emery@andela.com',
            'password': 'secret',
            'confirm_password': 'secret'
        }
        self.exist_user = {
            'username': 'Kudo',
            'email': 'kaka@andela.com',
            'password': 'secret',
            'confirm_password': 'secret'
        }
        self.business_data = {
            'name': 'Inzora rooftop coffee',
            'description': 'We have best coffee for you,',
            'category':'Coffee-shop',
            'country': 'Kenya',
            'city': 'Nairobi'
        }
        # Business sample data
        self.rev_business_data = {
            'name': 'KFC',
            'description': 'Finger lickin\' good',
            'category':'Food',
            'country': 'Kenya',
            'city': 'Nairobi'
        }
        with self.main.test_request_context():
            # Orphan id: User id that will be used to create an orphan token
            orphan_user = User(
                username="unamegg",
                email="anyemail@gmail.com",
                password=self.sample_user['password']
            )
            user = User(
                username=self.sample_user['username'],
                email=self.sample_user['email'],
                password=generate_password_hash(self.sample_user['password'])
            )
            db.session.add(user)
            db.session.add(orphan_user)
            db.session.commit()
            self.sample_user['id'] = user.id
            self.orphan_id = orphan_user.id
            db.session.remove()
            token = Token(user_id=self.sample_user['id'], access_token=get_token(
                self.sample_user['id']))
            orphan_token = Token(
                user_id=self.orphan_id, access_token=get_token(self.orphan_id))
            expired_token = Token(user_id=self.sample_user['id'], access_token=get_token(
                self.sample_user['id'], -3600))
            # Create bad signature token
            # Bad signature: #nt secret key from the one used in our API used
            # to hash tokens
            other_signature_token = Token(user_id=self.sample_user['id'], access_token=get_token(
                self.sample_user['id'], 3600, 'other_signature'))
            business = Business(
                user_id=self.sample_user['id'],
                name=self.rev_business_data['name'],
                description=self.rev_business_data['description'],
                category=self.rev_business_data['category'],
                country=self.rev_business_data['country'],
                city=self.rev_business_data['city'],
            )
            db.session.add(token)
            db.session.add(orphan_token)
            db.session.add(expired_token)
            db.session.add(other_signature_token)
            db.session.add(business)
            db.session.commit()
            self.test_token = token.access_token
            self.expired_test_token = expired_token.access_token
            self.other_signature_token = other_signature_token.access_token
            self.orphan_token = orphan_token.access_token

    def add_business(self):
        """
            Add sample business in database
        """
        business = Business(
            user_id=self.sample_user['id'],
            name=self.business_data['name'],
            description=self.business_data['description'],
            category=self.business_data['category'],
            country=self.business_data['country'],
            city=self.business_data['city'],
        )
        db.session.add(business)
        db.session.commit()
        self.business_data['hashid'] = business.hashid()
        self.business_data['id'] = business.id

    def tearDown(self):
        with self.app_context:
            db.session.remove()
            db.drop_all()
