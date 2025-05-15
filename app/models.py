from datetime import datetime
import hashlib
import os
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db



CSV_FILE = "fuel_prices_april_full.csv"

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
    default_date_range = db.Column(db.String(16), default='7d')    # e.g. '7d','30d'
    default_location = db.Column(db.String(64), nullable=True)
    alert_threshold = db.Column(db.Float, nullable=True)
    alert_frequency = db.Column(db.String(16), default='daily') # e.g. 'realtime','daily','weekly'
    public_dashboard = db.Column(db.Boolean, default=False)
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

class UploadBatch(db.Model):
    __tablename__ = "upload_batches"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    filename      = db.Column(db.String(200), nullable=True)   # Original File Name
    description   = db.Column(db.String(200), nullable=True)   # User description

    user          = db.relationship("User", back_populates="uploads")
    prices        = db.relationship("FuelPrice", back_populates="batch", cascade="all, delete-orphan")


class FuelPrice(db.Model):
    __tablename__ = "fuel_prices"
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("upload_batches.id"), nullable=False, index=True)

    publish_date = db.Column(db.Date,    nullable=False, index=True)   # PUBLISH_DATE
    trading_name = db.Column(db.String(100), nullable=False)           # TRADING_NAME
    brand_description = db.Column(db.String(100), nullable=True)       # BRAND_DESCRIPTION
    product_description = db.Column(db.String(100), nullable=False)    # PRODUCT_DESCRIPTION
    product_price = db.Column(db.Float,   nullable=False)              # PRODUCT_PRICE

    address = db.Column(db.String(200), nullable=True)            # ADDRESS
    location = db.Column(db.String(100), nullable=True)           # LOCATION
    postcode = db.Column(db.String(20),  nullable=True)           # POSTCODE

    area_description = db.Column(db.String(100), nullable=True)   # AREA_DESCRIPTION
    region_description = db.Column(db.String(100), nullable=True, index=True)# REGION_DESCRIPTION

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    batch = db.relationship("UploadBatch", back_populates="prices")

    def __repr__(self):
        return (f"<FuelPrice {self.publish_date} {self.trading_name} "
                f"{self.product_description} ${self.product_price:.2f}>")
