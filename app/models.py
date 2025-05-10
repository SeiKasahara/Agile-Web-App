import hashlib
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os

CSV_FILE = "fuel_prices_april_full.csv"

class User(UserMixin):
    def __init__(self, first_name, last_name, username, email, password=None, verified=False, is_social_login=False):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.verified = verified
        self.is_social_login = is_social_login
        self.password_hash = None
        if password:
            self.set_password(password)

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
