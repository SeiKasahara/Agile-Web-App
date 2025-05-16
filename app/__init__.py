import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from app.models import db, User
from app.routes.main import main

from app.routes.auth import auth_bp, oauth
from app.routes.fuel_upload import fuel_upload_bp

from app.utils.mail import mail
from app.utils.error_handlers import register_error_handlers
from app.routes.dashboard import dashboard_bp
from app.routes.share import share_bp, share_view_bp

migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
        print("loading the development config")

    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Initialize the oauth
    oauth.init_app(app)
    # Initialize the mail sys
    mail.init_app(app)
    
    # Initialize Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register error handlers
    register_error_handlers(app)

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

    app.register_blueprint(share_bp)
    app.register_blueprint(share_view_bp)
    
    # Create the database if it doesn't exist
    with app.app_context():
        db.create_all()

    return app
