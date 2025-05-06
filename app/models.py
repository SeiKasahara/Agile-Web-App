import hashlib

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
db = SQLAlchemy()
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_social_login = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(256))
    email_verify_code = db.Column(db.String(6), nullable=True)
    email_verify_expiration = db.Column(db.DateTime, nullable=True)
    default_fuel_type = db.Column(db.String(32), default='Unleaded')
    default_date_range = db.Column(db.String(16), default='7d')    # e.g. '7d','30d'
    default_location = db.Column(db.String(64), nullable=True)
    alert_threshold = db.Column(db.Float, nullable=True)
    alert_frequency = db.Column(db.String(16), default='daily') # e.g. 'realtime','daily','weekly'
    public_dashboard = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        if hasattr(hashlib, "scrypt"):
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = generate_password_hash(
                password,
                method="pbkdf2:sha256",
                salt_length=8
            )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)