'''
    User test file
'''
from flask import json
from tests.test_api import MainTests
from api.models.password_reset import PasswordReset
from api.helpers import generate_reset_token
from api.models import db


class UserTests(MainTests):
    '''
        User features tests class
    '''

    def test_registration(self):
        '''
            Testing registration
        '''
        response = self.app.post(self.url_prefix + 'auth/register',
                                 data=json.dumps({
                                     'username': 'testfdfdkjndf',
                                     'email': 'test@tester.cd',
                                     'password': '123456',
                                     'confirm_password': '123456'
                                 }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'have been successfully registered', response.data)

    def test_exist_email_username(self):
        '''
            Testing registration existing exist email and username
        '''
        response = self.app.post(
            self.url_prefix + 'auth/register',
            data=json.dumps({
                'username': self.sample_user['username'],
                'email': self.sample_user['email'],
                'password': self.sample_user['password'],
                'confirm_password': self.sample_user['confirm_password']
            }
            ), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Email was taken', response.data)
        self.assertIn(b'Username was taken', response.data)

    def test_exist_username_no_email(self):
        '''
            Testing registration with different email and the same username
        '''
        response = self.app.post(
            self.url_prefix + 'auth/register',
            data=json.dumps({
                'username': self.sample_user['username'],
                'email': 'another@gmail.com',
                'password': self.sample_user['password'],
                'confirm_password': self.sample_user['confirm_password']
            }
            ), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Username was taken', response.data)

    def test_wrong_registration(self):
        '''
            Test registration with incomplete data
        '''
        response = self.app.post(
            self.url_prefix + 'auth/register',
            data=json.dumps({
                'username': 'dummy name',
                'confirm_password': self.exist_user['confirm_password']
            }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Please provide', response.data)

    def test_login(self):
        '''
            Testing login
        '''
        response = self.app.post(
            self.url_prefix + 'auth/login', data=json.dumps({
                'email': self.sample_user['email'],
                'password': self.sample_user['password']
            }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'successfully logged', response.data)

    def test_unconfirmed_email_check(self):
        '''
            Testing unconfirmed email check
        '''
        response = self.app.post(
            self.url_prefix + 'auth/login', data=json.dumps({
                'email': self.unconfirmed_user['email'],
                'password': self.unconfirmed_user['password']
            }), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'confirm your email address', response.data)

    def test_invalid_credentials(self):
        '''
            Testing for invalid credentials
        '''
        response = self.app.post(
            self.url_prefix + 'auth/login',
            data=json.dumps({
                'email': 'fakeanyemail@gmail.com',
                'password': 'anyinvalidpassword'
            }), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid email or password', response.data)

    def test_unconfirmed_email(self):
        '''
            Testing login with unconfirmed email
        '''
        response = self.app.post(
            self.url_prefix + 'auth/login',
            data=json.dumps({
                'email': self.unconfirmed_user['email'],
                'password': self.sample_user['password']
            }), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Please confirm your email address', response.data)

    def test_reconfirming_email(self):
        '''
            Testing reconfirming email
        '''
        response = self.app.post(
            self.url_prefix + 'auth/register',
            data=json.dumps({
                'username': self.unconfirmed_user['username'],
                'email': self.unconfirmed_user['email'],
                'password': '123456',
                'confirm_password': '123456'
            }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'This account is already registered', response.data)

    def test_incomplete_creds(self):
        '''
            Test registration with incomplete data
        '''
        response = self.app.post(self.url_prefix + 'auth/login',
                                 data=json.dumps({
                                     'email': 'dummy@dummy.com',
                                 }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Please provide', response.data)

    def test_logout(self):
        '''
            Test Logout
        '''
        response = self.app.post(
            self.url_prefix + 'auth/logout',
            data={}, headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have successfully logged out', response.data)

    def test_invalid_reset(self):
        '''
            Testing reset password email with invalid input
        '''
        response = self.app.post(self.url_prefix + 'auth/reset-password',
                                 data=json.dumps({
                                     'email': 'fdsfsfds'
                                 }),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide valid details', response.data)

    def test_non_exist_reset(self):
        '''
            Testing reset password email with invalid input
        '''
        response = self.app.post(self.url_prefix + 'auth/reset-password',
                                 data=json.dumps({
                                     'email': 'anyemail@youremail.com'
                                 }),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Email doesn\'t exist', response.data)

    def test_email_password_reset(self):
        '''
            Testing reset password email
        '''
        response = self.app.post(self.url_prefix + 'auth/reset-password',
                                 data=json.dumps({
                                     'email': self.sample_user['email']
                                 }),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            b'Check your email to reset password', response.data)

    def test_password_reset(self):
        '''
            Testing reset password with a token
        '''
        gen_token = generate_reset_token()
        token = PasswordReset(
            user_id=self.sample_user['id'], reset_token=gen_token)
        db.session.add(token)
        db.session().commit()
        response = self.app.post(
            self.url_prefix + 'auth/reset-password/'+gen_token,
            data=json.dumps({
                'email': self.sample_user['email'],
                'password': 'awesome',
                'confirm_password': 'awesome'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            b'You have successfully reset your password', response.data)

    def test_inv_reset_tok(self):
        '''
            Testing reset password with a invalid token
        '''
        response = self.app.post(
            self.url_prefix + 'auth/reset-password/dsaaq342',
            data=json.dumps({
                'email': self.sample_user['email'],
                'password': 'awesome',
                'confirm_password': 'awesome'
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Invalid reset token', response.data)

    def test_inv_password_reset(self):
        '''
            Testing reset password with a invalid input
        '''
        gen_token = generate_reset_token()
        token = PasswordReset(
            user_id=self.sample_user['id'], reset_token=gen_token)
        db.session.add(token)
        db.session().commit()
        response = self.app.post(
            self.url_prefix + 'auth/reset-password/'+gen_token,
            data=json.dumps({
                'email': self.sample_user['email'],
                'password': 'awesome',
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide valid details', response.data)

    def test_password_change(self):
        '''
            Testing changing password
        '''
        response = self.app.post(
            self.url_prefix + 'auth/change-password',
            data=json.dumps({
                'old_password': self.sample_user['password'],
                'new_password': '12345678'
            }),
            content_type='application/json',
            headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            b'You have successfully changed your password', response.data)

    def test_invalid_old_password_change(self):
        '''
            Testing password change with invalid old password
        '''
        response = self.app.post(
            self.url_prefix + 'auth/change-password',
            data=json.dumps({
                'old_password': 'sgdffsds', 'new_password': '123456'
            }),
            content_type='application/json',
            headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Invalid old password', response.data)

    def test_change_password_inv(self):
        '''
            Testing password Reset with invalid details
        '''
        response = self.app.post(self.url_prefix + 'auth/change-password',
                                 data=json.dumps({
                                     'new_password': '123456',
                                 }),
                                 content_type='application/json',
                                 headers={'Authorization': self.test_token})
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide valid details', response.data)

    def test_invalid_token(self):
        '''
            Testing invalid token
        '''
        # Test invalid token by accessing protected endpoint with invalid
        # authorization token
        response = self.app.post(
            self.url_prefix + 'auth/change-password',
            data={
                # Old password
                'old_password': self.sample_user['password'],
                'new_password': '123456'
            },
            headers={'Authorization': 'eyJhbGciOQxYI-vmeqW6'})
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            b'Unauthorized', response.data)

    def test_expired_token(self):
        '''
            Testing Expired token
        '''
        # Test expired token by accessing protected endpoint with expired token
        response = self.app.post(
            self.url_prefix + 'auth/change-password',
            data={
                # Old password
                'old_password': self.sample_user['password'],
                'new_password': '123456'
            },
            headers={'Authorization': self.expired_test_token})
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            b'Unauthorized', response.data)

    def test_bad_signature_token(self):
        '''
            Testing Bad signature token
        '''
        # Access protected endpoint with bad signature token
        response = self.app.get(
            self.url_prefix + 'account/businesses',
            headers={'Authorization': self.other_signature_token})
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            b'Unauthorize', response.data)

    def test_validation_methods(self):
        '''
            Test validation methods (same,minimum,email,string)
        '''
        response = self.app.post(
            self.url_prefix + 'auth/register',
            data=json.dumps({
                'username': '@@',
                'email': 'sdfs',
                'password': '123',
                'confirm_password': '123456789'
            }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid email address', response.data)
        self.assertIn(b'should be string', response.data)
        self.assertIn(b'don\'t match', response.data)
        self.assertIn(b'should not be less', response.data)

    def test_other_validation_methods(self):
        '''
            Test validation methods (required,maximum)
        '''
        response = self.app.post(
            self.url_prefix + 'auth/register',
            data=json.dumps({
                'username': None,
                'password': 'sgfdcasfgcdfagsdasfdgascgdfcasfd',
                'confirm_password': 'sgfdcasfgcdfagsdasfdgascgdfcasfd'
            }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'is required', response.data)
        self.assertIn(b'should not be greater', response.data)

    def test_invalid_confirm(self):
        '''
            Testing email confirmation with invalid email
        '''
        response = self.app.post(self.url_prefix + 'auth/confirm/bfsd',
                                 data=json.dumps({
                                     'email': 'fdsfsfds'
                                 }),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Please provide valid details', response.data)

    def test_invalid_link_token_confirm(self):
        '''
            Testing email confirmation with invalid token
        '''
        response = self.app.post(self.url_prefix + 'auth/confirm/bfsd',
                                 data=json.dumps({
                                     'email': self.unconfirmed_user['email']
                                 }),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            b'Invalid confirm link token or email', response.data)

    def test_email_confirm(self):
        '''
            Test if email email confirmation token exist
        '''
        response = self.app.post(self.url_prefix + 'auth/confirm/'+(
            self.unconfirmed_user['activation_token']),
            data=json.dumps({
                'email': self.unconfirmed_user['email']
            }),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Your email was confirmed', response.data)

    def test_confirm_invalid_token(self):
        '''
            Test trying to confirm invalid confirm token
        '''
        response = self.app.post(
            self.url_prefix + 'auth/confirm-token',
            data=json.dumps(
                {'token': 'anyinvalidtoken'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_confirm_confirm_token(self):
        '''
            Test trying to confirm invalid confirm token
        '''
        response = self.app.post(
            self.url_prefix + 'auth/confirm-token',
            data=json.dumps(
                {'token': self.unconfirmed_user['activation_token']}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_confirm_empty_token(self):
        '''
            Test trying to confirm invalid empty token
        '''
        response = self.app.post(
            self.url_prefix + 'auth/confirm-token',
            data=json.dumps(
                {}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_unconfirmed_email_middleware(self):
        '''
            Test unconfirmed email middleware
        '''
        response = self.app.get(
            self.url_prefix + 'account/businesses?',
            headers={'Authorization': self.unconfirmed_user_token})
        self.assertEqual(response.status_code, 401)
