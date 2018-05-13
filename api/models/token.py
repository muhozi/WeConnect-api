""" Access tokens Model """
from api import db


class Token(db.Model):
    """Access tokens Model"""

    __tablename__ = "access_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_token = db.Column(db.String, nullable=False)
    expires_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False)
    created_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(),
                           server_onupdate=db.func.now(), nullable=False)
