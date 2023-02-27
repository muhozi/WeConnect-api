'''
    Helper Methods
'''
import secrets
import time
from flask_mail import Message
from hashids import Hashids
from authlib.jose import jwt
from authlib.jose.errors import ExpiredTokenError
from itsdangerous import (URLSafeTimedSerializer as Serializer)
from flask import current_app as app
from api.conf import mail


def get_token(user_id, expires_in=3600):
    '''
        Generate token helper function
    '''
    header = {'alg': 'RS256'}
    payload = {
        'id': user_id,
        'exp': int(time.time() + expires_in)
    }
    token = jwt.encode(header, payload, app.config['PRIVATE_KEY'])
    token = token.decode()
    return token


def token_id(token):
    '''
        Check token if token is valid this returns ID aapended to it
    '''
    try:
        claims = jwt.decode(token, app.config['PUBLIC_KEY'])
        claims.validate()
    except ExpiredTokenError:
        return False
    except:
        return False
    return claims['id']


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


def get_confirm_email_token(email, key=None):
    '''
        Generate confirm link token
    '''
    if key is None:
        key = app.config['SECRET_KEY']
    token = Serializer(key)
    return token.dumps(email)


def send_mail(subject, email, body):
    ''' Send reset password email '''
    msg = Message(subject, sender=(
        'We Connect', 'noreply@weconnect.com'), recipients=[email])
    msg.html = body
    mail.send(msg)
