""" User Model """
from api import db
from api.helpers import hashid, get_id


class Business(db.Model):
    """Users Model"""

    __tablename__ = "businesses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), index=False, nullable=False)
    description = db.Column(db.Text, index=False, nullable=False)
    country = db.Column(db.String(128), index=False, nullable=False)
    city = db.Column(db.String(128), index=False, nullable=False)
    category = db.Column(db.String(128), index=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(),
                           server_onupdate=db.func.now(), nullable=False)

    def hashid(self):
        """
            Generate hashid
        """
        return hashid(self.id)

    @classmethod
    def get(cls, business_id):
        """
            Get business by hashid
        """ 
        found_id = get_id(business_id)
        if found_id is not None:
            return cls.query.get(found_id)

    @classmethod
    def serializer(cls, datum):
        """ 
            Serialize model object array (Convert into a list
        """
        results = []
        for data in datum:
            obj = {
                'id': hashid(data.id),
                'user_id': hashid(data.user_id),
                'name': data.name,
                'description': data.description,
                'category': data.category,
                'country': data.country,
                'city': data.city,
                'created_at': data.created_at,
            }
            results.append(obj)
        return results

    @classmethod
    def get_by_user(cls, business_id, user_id):
        """ Get user businesses """
        found_business_id = get_id(business_id)
        if get_id(business_id) is not None:
            return cls.query.filter_by(user_id=user_id, id=found_business_id).first()

    @classmethod
    def serialize_obj(cls, data):
        """ Convert model object to dictionary """
        return {
            'id': hashid(data.id),
            'user_id': hashid(data.user_id),
            'name': data.name,
            'description': data.description,
            'country': data.country,
            'city': data.city,
            'created_at': data.created_at,
        }

    @classmethod
    def user_businesses(cls, user_id):
        """ Retrieve user's businesses"""
        businesses = cls.query.filter_by(user_id=user_id).all()
        if businesses is not None:
            return businesses

    @classmethod
    def has_two_same_business(cls, user_id, business_name, business_id):
        """ Check if the user has the two same busines name #nt from the one to update"""
        if cls.query.filter(cls.user_id==user_id, cls.name == business_name, cls.id != get_id(business_id)).first() is not None:
            return True
        return False

    @classmethod
    def update(cls, business_id, data):
        """ Update business"""
        business = cls.query.filter_by(id=get_id(business_id)).first()
        business.name = data['name']
        business.description = data['description']
        business.category = data['category']
        business.city = data['city']
        business.country = data['country']
        db.session.add(business)
        db.session.commit()
