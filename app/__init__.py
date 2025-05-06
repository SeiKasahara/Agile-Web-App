import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models import db, User
from app.routes.main import main

from app.routes.auth import auth_bp
from app.fuel_upload import fuel_upload_bp

from app.utils.mail import mail
from app.routes.dashboard import dashboard_bp

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
        print("loading the development config")

    # Initialize the oauth
    oauth.init_app(app)
    # Initialize the mail sys
    mail.init_app(app)
    
    # Initialize Database
    db.init_app(app)
    migrate.init_app(app, db)
    

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)

    app.register_blueprint(fuel_upload_bp)

    app.register_blueprint(dashboard_bp)
    
    # Create the database if it doesn't exist
    with app.app_context():
        db.create_all()

    return app
