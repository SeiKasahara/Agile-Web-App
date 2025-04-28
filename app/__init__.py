import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import db, User
from app.routes import register_routes
from app.routes.main import main
from app.routes.auth import auth_bp


def create_app():
    app = Flask(__name__)

    # Basic configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, '..', 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']  = False

    # Initialize Database
    db.init_app(app)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Routes
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)

    # Create the database if it doesn't exist
    with app.app_context():
        db.create_all()
    return app