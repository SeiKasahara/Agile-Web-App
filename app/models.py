from datetime import datetime
import hashlib
import os
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Used for CSV backup functionality
CSV_FILE = "fuel_prices_april_full.csv"

# --------------------- USER MODEL --------------------- #
class User(db.Model, UserMixin):
    __tablename__ = "users"
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
    default_date_range = db.Column(db.String(16), default='7d')
    default_location = db.Column(db.String(64), nullable=True)
    public_dashboard = db.Column(db.Boolean, default=False)
    share_expire_range = db.Column(db.String(16), default='7d')

    uploads = db.relationship("UploadBatch", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save_to_csv(self):
        data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
            "verified": self.verified,
            "is_social_login": self.is_social_login,
            "password_hash": self.password_hash
        }
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        else:
            df = pd.DataFrame([data])
        df.to_csv(CSV_FILE, index=False)

    @classmethod
    def get_user_by_email(cls, email):
        if not os.path.exists(CSV_FILE):
            return None
        df = pd.read_csv(CSV_FILE)
        user_data = df[df["email"] == email]
        if not user_data.empty:
            user_row = user_data.iloc[0]
            user = cls(
                first_name=user_row["first_name"],
                last_name=user_row["last_name"],
                username=user_row["username"],
                email=user_row["email"],
                verified=user_row["verified"],
                is_social_login=user_row["is_social_login"]
            )
            user.password_hash = user_row["password_hash"]
            return user
        return None

# --------------------- STATION MODEL --------------------- #
class Station(db.Model):
    __tablename__ = "stations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(255), nullable=True)

    # Define relationships if needed
    # Example:
    # prices = db.relationship('PriceRecord', backref='station', lazy=True)

    def __repr__(self):
        return f"<Station {self.name}>"

# --------------------- UPLOAD BATCH MODEL --------------------- #
class UploadBatch(db.Model):
    __tablename__ = "upload_batches"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    filename = db.Column(db.String(200), nullable=True)

    user = db.relationship("User", back_populates="uploads")
    prices = db.relationship("PriceRecord", back_populates="batch", cascade="all, delete-orphan")

# --------------------- PRICE RECORD MODEL --------------------- #
class PriceRecord(db.Model):
    __tablename__ = "price_records"
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("upload_batches.id"), nullable=False)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey("fuel_types.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    batch = db.relationship("UploadBatch", back_populates="prices")
    fuel_type = db.relationship("FuelType", back_populates="price_records")

# --------------------- FUEL TYPE MODEL --------------------- #
class FuelType(db.Model):
    __tablename__ = "fuel_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    price_records = db.relationship("PriceRecord", back_populates="fuel_type")
