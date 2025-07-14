from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from datetime import timedelta

load_dotenv()

app = Flask(__name__, )
app.config.from_object('config')
app.config.setdefault('SQLALCHEMY_DATABASE_URI', os.getenv('DB_URL'))
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Access token expiration
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Refresh token expiration
app.config['JWT_IDENTITY_CLAIM'] = 'sub'  # Specify the claim used for user identity
app.config['JWT_USER_CLAIM'] = 'roles'  # Specify the claim used for user roles
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')  # Change this to a secure key
csrf = CSRFProtect()
csrf.init_app(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager() 
jwt.init_app(app)


from config import secret
app.secret_key = secret
migrate = Migrate(app, db)

from pkg import routes, telemed_routes
