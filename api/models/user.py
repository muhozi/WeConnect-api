''' User Model '''
from api.models import db
from api.helpers import get_confirm_email_token


class User(db.Model):
    '''Users Model'''

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=False,
                         unique=True, nullable=False)
    email = db.Column(db.String(120), index=False, unique=True, nullable=False)
    activation_token = db.Column(db.String(128), nullable=True)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(
        db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(
    ), server_onupdate=db.func.now(), nullable=False)

    @classmethod
    def save(cls, user):
        '''
            Save user
        '''
        save_user = cls(
            username=user['username'],
            email=user['email'],
            activation_token=(get_confirm_email_token(
                user['email']) if 'confirm_token' not in user else user.get('confirm_token')),
            password=user['password']
        )
        db.session.add(save_user)
        db.session.commit()

    @classmethod
    def get_user(cls, email):
        '''Check if user exists and return user details'''
        user = User.query.filter_by(email=email).first()
        return user

    @classmethod
    def update_password(cls, user_id, password):
        '''
            Update password
        '''
        user = cls.query.get(user_id)
        user.password = password
        db.session.add(user)
        db.session.commit()

    @classmethod
    def update_token(cls, user_id, token):
        ''' Update business'''
        user = cls.query.filter_by(id=user_id).first()
        user.activation_token = token
        db.session.add(user)
        db.session.commit()

    @classmethod
    def activate(cls, user_id):
        '''
            Update password
        '''
        user = cls.query.get(user_id)
        user.activation_token = None
        db.session.add(user)
        db.session.commit()
