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
from app.routes.share import share_bp

# Flask-Migrate for database migrations
migrate = Migrate()
# CSRF protection for forms and APIs
csrf = CSRFProtect()


def create_app():
    # Create Flask app instance
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'development')
    # Load configuration based on environment
    if env == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
        print("loading the development config")

    # Initialize CSRF protection
    csrf.init_app(app)

    # Initialize OAuth for social login
    oauth.init_app(app)
    # Initialize mail system for sending emails
    mail.init_app(app)

    # Initialize database connection and migration support
    db.init_app(app)
    migrate.init_app(app, db)

    # Register global error handlers
    register_error_handlers(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Return the user object based on user_id for Flask-Login
        return User.query.get(int(user_id))

    # Register main blueprint (root routes)
    app.register_blueprint(main)
    # Register authentication blueprint
    app.register_blueprint(auth_bp)
    # Register fuel upload blueprint
    app.register_blueprint(fuel_upload_bp)
    # Register dashboard blueprint
    app.register_blueprint(dashboard_bp)
    # Register share blueprint
    app.register_blueprint(share_bp)

    # Create database tables if they do not exist (only on startup)
    with app.app_context():
        db.create_all()

    return app
