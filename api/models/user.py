""" User Model """
from api import db


class User(db.Model):
    """Users Model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=False,
                         unique=True, nullable=False)
    email = db.Column(db.String(120), index=False, unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(
        db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(
    ), server_onupdate=db.func.now(), nullable=False)

    @classmethod
    def get_user(cls, email):
        """Check if user exists and return user details"""
        user = User.query.filter_by(email=email).first()
        return user
