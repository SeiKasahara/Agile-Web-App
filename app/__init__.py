import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models import db, User
from app.routes.auth import auth_bp, oauth
from app.routes.main import main

from app.routes.auth import auth_bp
from app.fuel_upload import fuel_upload_bp

from app.utils.mail import mail
from app.routes.dashboard import dashboard_bp

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'development')
    
    # Load the correct config based on the environment
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
        print("Loading the development config")

    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize the login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize OAuth (from auth.py)
    oauth.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main)
    app.register_blueprint(fuel_upload_bp)
    app.register_blueprint(dashboard_bp)

    # Create the database if it doesn't exist
    with app.app_context():
        db.create_all()

    return app
