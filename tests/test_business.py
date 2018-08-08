'''
    Business features tests
'''
from flask import json
from tests.test_api import MainTests
from api.models import db
from api.models.business import Business


class BusinessTests(MainTests):
    '''
        Business tests class
    '''

    def test_no_businesses(self):
        '''
            Test retrieving businesses with none registered
        '''
        business = Business.query.filter_by(id=1).first()
        db.session.delete(business)
        db.session.commit()
        response = self.app.get(
            self.url_prefix + 'businesses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'No business found', response.data)

    def test_business_registration(self):
        '''
            Testing business registration
        '''
        response = self.app.post(
            self.url_prefix + 'businesses',
            data=json.dumps({
                'name': 'Inzora rooftop coffee',
                'description': 'We have best coffee',
                'category': 'Coffee-shop',
                'country': 'Kenya',
                'city': 'Nairobi'
            }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            b'business has been successfully registered', response.data)

    def test_same_business_registration(self):
        '''
            Test business registration with the same name under same user
        '''
        response = self.app.post(
            self.url_prefix + 'businesses', data=json.dumps({
                'user_id': self.sample_user['id'],
                'name': self.rev_business_data['name'],
                'description': self.rev_business_data['description'],
                'category': self.rev_business_data['category'],
                'country': self.rev_business_data['country'],
                'city': self.rev_business_data['city'],
            }), headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'You have already registered business with the same name',
            response.data)

    def test_business_with_invalid_data(self):
        '''
            Testing business registration with invalid data
        '''
        response = self.app.post(self.url_prefix + 'businesses',
                                 data=json.dumps({
                                     'description': 'We have best coffee, ',
                                     'country': 'Kenya',
                                     'city': 'Nairobi'
                                 }),
                                 headers={'Authorization': self.test_token},
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide required info', response.data)

    def test_business_deletion(self):
        '''
            Test removing business
        '''
        self.add_business()
        response = self.app.delete(
            self.url_prefix + 'businesses/' + self.business_data['hashid'],
            data={}, headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 202)
        self.assertIn(
            b'Your business has been successfully deleted', response.data)

    def test_no_priv_business_deletion(self):
        '''
            Test removing business without privileges to it
        '''
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save business in the storage list for testing
        self.add_business()
        response = self.app.delete(
            self.url_prefix + 'businesses/' +
            self.business_data['hashid'],
            data={},
            headers={'Authorization': self.orphan_token})
        self.assertEqual(response.status_code, 400)

    def test_business_update(self):
        '''
            Test business updating
        '''
        # New business details to test updating
        new_business_data = {
            'name': 'TRM',
            'description': 'We got them all',
            'category': 'Mall',
            'country': 'Kenya',
            'city': 'Nairobi'
        }
        # Add user(owner) to the business data dict
        self.add_business()
        response = self.app.put(
            self.url_prefix + 'businesses/' + self.business_data['hashid'],
            data=json.dumps(new_business_data),
            headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 202)
        self.assertIn(
            b'Your business has been successfully updated', response.data)

    def test_no_priv_business_update(self):
        '''
            Test business updating with no privileges to it
        '''
        # New business details to test updating
        self.add_business()
        new_business_data = {
            'name': 'Wazi wazi',
            'description': 'Wear yours',
            'country': 'Kenya',
            'city': 'Nakuru'
        }
        # Add user(owner) to the business data dict
        response = self.app.put(
            self.url_prefix + 'businesses/' + self.business_data['hashid'],
            data=json.dumps(new_business_data),
            headers={'Authorization': self.orphan_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'This business doesn\'t exist or you don\'t have',
            response.data)

    def test_exist_name_business(self):
        '''
            Test business updating with existing busiiness name under one user
        '''
        self.add_business()
        # Data to be saved to test same name businesses under one person
        new_business_data = {
            'user_id': self.sample_user['id'],
            'name': 'TRM',
            'description': 'Enjoy Coffee and Pizzas',
            'category': 'Mall',
            'country': 'Kenya',
            'city': 'Nakuru'
        }
        business = Business(
            user_id=self.sample_user['id'],
            name='TRM',
            description=self.business_data['description'],
            category=self.business_data['category'],
            country=self.business_data['country'],
            city=self.business_data['city'],
        )
        db.session.add(business)
        db.session.commit()
        response = self.app.put(
            self.url_prefix + 'businesses/' + self.business_data['hashid'],
            data=json.dumps(new_business_data),
            headers={'Authorization': self.test_token},
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'You have already registered a business with same name',
            response.data)

    def test_invalid_data_business_upd(self):
        '''
            Test business updating with invalid data
        '''
        # New business details to test updating
        new_business_data = {
            'name': 'Inzora Nakuru',
            'country': 'Kenya',
            'city': 'Nakuru'
        }
        self.add_business()
        response = self.app.put(
            self.url_prefix + 'businesses/' + self.business_data['hashid'],
            data=json.dumps(new_business_data),
            headers={'Authorization': self.test_token},
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide required info', response.data)

    def test_no_user_businesses(self):
        '''
            Test retrieving logged in user business without any
        '''
        response = self.app.get(
            self.url_prefix + 'account/businesses',
            headers={'Authorization': self.orphan_token})
        self.assertIn(
            b'You don\'t have any registered business', response.data)

    def test_user_businesses(self):
        '''
            Test retrieving logged in user business
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'account/businesses?name=' +
            self.business_data['name'] +
            '&country='+self.business_data['country'] +
            '&city='+self.business_data['city'] +
            '&category='+self.business_data['category'] +
            '&limit=1' +
            '&page=1', headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 200)

    def test_user_businesses_search(self):
        '''
            Test bad search logged in user business
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'account/businesses?name=' +
            self.business_data['name'] +
            '&country=unknownCountry_g',
            headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'No business found', response.data)

    def test_acc_bad_params_businesses(self):
        '''
            Test invalid search of logged in user business
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'account/businesses?&limit=' +
            '&page=notInt', headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide valid details', response.data)

    def test_search_filters(self):
        '''
            Test business search and filters
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'businesses?name='+self.business_data['name'] +
            '&country='+self.business_data['country'] +
            '&city='+self.business_data['city'] +
            '&category='+self.business_data['category'] +
            '&limit='+'1' +
            '&page=1'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'businesses found', response.data)

    def test_search_all_filters(self):
        '''
            Test search all businesses by all keywords
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'businesses?name='+self.business_data['name'] +
            '&searchAll=true' +
            '&limit='+'1' +
            '&page=1'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'businesses found', response.data)

    def test_user_businesses_invalid_limit_number(self):
        '''
            Test getting user businesses with invalid page details
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'businesses?name='+self.business_data['name'] +
            '&searchAll=true' +
            '&limit='+'fhsjbjh' +  # Invalid page limit number
            '&page=bhjdbfs'  # Invalid page number
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'businesses found', response.data)

    def test_invalid_page_params(self):
        '''
            Test retrieving business with invalid params
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'businesses?' +
            'limit='+'notInt' +
            '&page=notInt'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide valid details', response.data)

    def test_all_businesses(self):
        '''
            Test retrieving all registered businesses
        '''
        self.add_business()
        # Add user(owner) to the business data dict
        self.business_data['user_id'] = self.sample_user['id']
        # Save businesses to test
        response = self.app.get(
            self.url_prefix + 'businesses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'businesses found', response.data)

    def test_empty_businesses(self):
        '''
            Test retrieving businesses with none registered
        '''
        business = Business.query.filter_by(id=1).first()
        db.session.delete(business)
        db.session.commit()
        response = self.app.get(
            self.url_prefix + 'businesses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No business found!', response.data)

    def test_business(self):
        '''
            Test retrieving business details
        '''
        self.add_business()
        response = self.app.get(
            self.url_prefix + 'businesses/' + self.business_data['hashid'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Business found', response.data)

    def test_non_exist_business(self):
        '''
            Test retrieving business details which doesn't exist
        '''
        response = self.app.get(
            self.url_prefix + 'businesses/' + "fsdfsd")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Business not found', response.data)
