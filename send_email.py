import ssl
from api.models.business import Business
from api import create_app
from api import db
from flask_sendgrid import SendGrid
ssl._create_default_https_context = ssl._create_unverified_context
app = create_app('development')
mail = SendGrid(app)
with app.app_context():
    mail.send_email(
        from_email='noreply@allconnect.heroku.com',
        to_email='muhozie@gmail.com',
        subject='We Connect application',
        text='Hello Emery, I\'m just testing from my We Connect',
    )