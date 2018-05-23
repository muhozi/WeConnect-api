"""
    Helper Methods
"""
import secrets
from flask_mail import Message
from api import mail
from flask import current_app as app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired, URLSafeSerializer)
from hashids import Hashids


def get_token(user_id, expires_in=3600, key=None):
    """"
        Generate token helper function
    """
    if key is None:
        key = app.config['SECRET_KEY']
    token = Serializer(key, expires_in)
    token_with_id = token.dumps({'id': user_id})
    return token_with_id.decode('ascii')


def token_id(token):
    """
        Check token if token is valid this returns ID aapended to it
    """
    deserialize_token = Serializer(app.config['SECRET_KEY'])
    try:
        data = deserialize_token.loads(token)
    except SignatureExpired:
        return False  # valid token, but expired
    except BadSignature:
        return False  # invalid token
    return data['id']


def hashid(id_string):
    """
        Generate hashid
    """
    hashid = Hashids(salt=app.config['SECRET_KEY'], min_length=34)
    return hashid.encode(id_string)


def get_id(id_string):
    """
        Get id from hashid
    """
    hashid = Hashids(salt=app.config['SECRET_KEY'], min_length=34)
    f_id = hashid.decode(id_string)
    if len(f_id) is not 0:
        return f_id[0]
    return None


def generate_reset_token():
    return secrets.token_urlsafe(84)


def send_mail(body, email):

    msg = Message('Reset your account password',
                  body=body,
                  sender=('We Connect', 'noreply@allconnect.herokuapp.com'),
                  recipients=[email],
                  )
    mail.send(msg)
