""" User Model """
from api import db
from api.helpers import hashid


class Review(db.Model):
    """Users Model"""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), index=False, nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey(
        'businesses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(),
                           server_onupdate=db.func.now(), nullable=False)

    @classmethod
    def serializer(cls, datum):
        """ Serialize model object array (Convert into a list) """
        results = []
        for data in datum:
            obj = {
                'id': hashid(data.id),
                'user_id': hashid(data.user_id),
                'description': data.description,
                'created_at': data.created_at,
            }
            results.append(obj)
        return results
