from faker import Faker
from api.models.business import Business
from api.index import create_app
from api.index import db

app = create_app('development')
fake = Faker()
with app.app_context():
    businesses = []
    for _ in range(100):
        business = Business(
            user_id=1,
            name=fake.company(),
            description=fake.text(max_nb_chars=300, ext_word_list=None),
            category=fake.job(),
            country=fake.country(),
            city=fake.city(),
        )
        db.session.add(business)
        db.session.commit()
        businesses.append(business)
