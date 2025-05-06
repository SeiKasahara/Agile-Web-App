from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

from app.models import FuelPrice

# Blueprint for modular route handling
fuel_upload_bp = Blueprint('fuel_upload', __name__)

# Get app context
from app import db

# Ensure uploads folder exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to handle CSV upload
@fuel_upload_bp.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Read CSV and insert into DB
    try:
        df = pd.read_csv(filepath)
        for _, row in df.iterrows():
            entry = FuelPrice(
                city=row['city'],
                region=row['region'],
                fuel_type=row['type_name'],
                price_per_litre=row['price_per_litre'],
                price_date=row['price_date']
            )
            db.session.add(entry)
        db.session.commit()
        return jsonify({"message": "File uploaded and data saved successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
