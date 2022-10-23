from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)

# Flask WTF
app.config['SECRET_KEY'] = '6607fd26d3df259abdbd181d3d3c90e9'

# Connect To The DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Connect to Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'sign_in' # redirecting all unauthorised users to the login page.
login_manager.login_message_category = 'info' # changing category of error messages for unauthorised users

# connect to Mail flask_mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] =  os.environ.get('FLASK_MAIL_USERNAME')
app.config['MAIL_PASSWORD'] =  os.environ.get('FLASK_MAIL_PASSWORD')
mail = Mail(app)

from flask_blog import routes
