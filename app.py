"""
	Main file to run the app
"""
import os
from api.api import User, Business, Review
from api import create_app,db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = create_app('development')
migrate = Migrate(app, db)
if __name__ == '__main__':
    # Run the application
    app.run()