""" Password reset Model """
from api import db


class PasswordReset(db.Model):
    """assword reset Model class"""

    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reset_token = db.Column(db.String, nullable=False)
    expires_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False)
    created_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(),
                           server_onupdate=db.func.now(), nullable=False)
