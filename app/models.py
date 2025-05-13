from datetime import datetime
import hashlib

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
db = SQLAlchemy()
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
    
class UploadBatch(db.Model):
    __tablename__ = "upload_batches"
    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    filename      = db.Column(db.String(200), nullable=True)   # Original File Name

    user          = db.relationship("User", back_populates="uploads")
    prices        = db.relationship("PriceRecord", back_populates="batch", cascade="all, delete-orphan")

class Station(db.Model):
    __tablename__ = 'stations'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    address        = db.Column(db.String(200), nullable=False)
    suburb         = db.Column(db.String(100), nullable=True)
    postcode       = db.Column(db.String(20), nullable=True)
    area           = db.Column(db.String(100), nullable=True)
    region         = db.Column(db.String(100), nullable=True, index=True)
    latitude       = db.Column(db.Float, nullable=True)
    longitude      = db.Column(db.Float, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('address','postcode', name='uq_station_address'),
    )

    prices = db.relationship('PriceRecord', back_populates='station')

class FuelType(db.Model):
    __tablename__ = 'fuel_types'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    prices = db.relationship('PriceRecord', back_populates='fuel_type')

class PriceRecord(db.Model):
    __tablename__ = 'price_records'
    id            = db.Column(db.Integer, primary_key=True)
    station_id    = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False, index=True)
    fuel_type_id  = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    date          = db.Column(db.Date, nullable=False, index=True)
    price         = db.Column(db.Float, nullable=False)
    batch_id      = db.Column(
                       db.Integer,
                       db.ForeignKey("upload_batches.id"),
                       nullable=False,
                       index=True
                    )
    batch         = db.relationship("UploadBatch", back_populates="prices")
    station       = db.relationship('Station', back_populates='prices')
    fuel_type     = db.relationship('FuelType', back_populates='prices')

class SharedReport(db.Model):
    id                   = db.Column(db.Integer, primary_key=True)
    user_id              = db.Column(db.Integer, db.ForeignKey('users.id'))
    fuel_type            = db.Column(db.String(50))
    location             = db.Column(db.String(50))
    date                 = db.Column(db.String(10))
    forecast_config      = db.Column(db.Text)
    heatmap_points_json  = db.Column(db.Text)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)