''' Review Model '''
from api.models import db
from api.models.user import User
from api.helpers import hashid


class Review(db.Model):
    '''Review Model'''

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
    def save(cls, data):
        '''
            Save method
        '''
        review = cls(
            user_id=data['user_id'],
            description=data['description'],
            business_id=data['business_id']
        )
        db.session.add(review)
        db.session.commit()
        return review

    @classmethod
    def serializer(cls, datum):
        ''' Serialize model object array (Convert into a list) '''
        results = []
        for data in datum:
            obj = {
                'id': hashid(data.id),
                'user': User.query.get(data.user_id).username.capitalize(),
                'description': data.description,
                'created_at': data.created_at,
            }
            results.append(obj)
        return results

    @property
    def serialize_one(self):
        ''' Serialize model object array (Convert into a list) '''
        obj = {
            'id': hashid(self.id),
            'user': User.query.get(self.user_id).username.capitalize(),
            'description': self.description,
            'created_at': self.created_at,
        }
        return obj

    @classmethod
    def delete_all(cls, business_id):
        '''
            Delete All reviews about business
        '''
        cls.query.filter_by(business_id=business_id).delete()
