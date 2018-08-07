'''
    Helper Methods
'''
import secrets
from flask_mail import Message
from hashids import Hashids
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask import current_app as app
from api.conf import mail


def get_token(user_id, expires_in=3600, key=None):
    '''
        Generate token helper function
    '''
    if key is None:
        key = app.config['SECRET_KEY']
    token = Serializer(key, expires_in)
    token_with_id = token.dumps({'id': user_id})
    return token_with_id.decode('ascii')


def token_id(token):
    '''
        Check token if token is valid this returns ID aapended to it
    '''
    deserialize_token = Serializer(app.config['SECRET_KEY'])
    try:
        data = deserialize_token.loads(token)
    except SignatureExpired:
        return False  # valid token, but expired
    except BadSignature:
        return False  # invalid token
    return data['id']


def hashid(id_string):
    '''
        Generate hashid
    '''
    hash_id = Hashids(salt=app.config['SECRET_KEY'], min_length=34)
    return hash_id.encode(id_string)


def get_id(id_string):
    '''
        Get id from hashid
    '''
    hash_id = Hashids(salt=app.config['SECRET_KEY'], min_length=34)
    f_id = hash_id.decode(id_string)
    if len(f_id) is not 0:
        return f_id[0]
    return None


def generate_reset_token():
    ''' Generate reset password token '''
    return secrets.token_urlsafe(84)


def get_confirm_email_token(expires_in=3600, key=None):
    '''
        Generate confirm link token
    '''
    if key is None:
        key = app.config['SECRET_KEY']
    token = Serializer(key, expires_in)
    return token.dumps({}).decode('ascii')


def send_mail(email, body):
    ''' Send resrt password email '''
    msg = Message('Reset your account password on WeConnect',
                  sender=('We Connect', 'noreply@allconnect.herokuapp.com'),
                  recipients=[email]
                  )
    msg.html = body
    mail.send(msg)
