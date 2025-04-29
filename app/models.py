import hashlib

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
db = SQLAlchemy()
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

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