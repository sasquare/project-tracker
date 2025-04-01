from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from database import db
import os

# Load environment variables from .env in development
load_dotenv()

app = Flask(__name__)

# Use environment variables for production, fallback to .env for local dev
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///projects.db')  # Fallback to SQLite locally
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Replace 'sqlite:///' with 'postgresql://' for Render compatibility
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
    pass  # Keep SQLite for local dev
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://')

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User
from routes import *

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)