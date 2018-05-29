""" Access tokens Model """
from api.models import db


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

    @classmethod
    def save(cls, data):
        """
            Save access token
        """
        token = cls(
            user_id=data['user_id'],
            access_token=data['access_token'],
        )
        db.session.add(token)
        db.session.commit()

    @classmethod
    def delete(cls, token_id):
        """
            Delete token
        """
        token = Token.query.get(token_id)
        db.session.delete(token)
        db.session.commit()
