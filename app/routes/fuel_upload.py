import re
import os, secrets
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import numpy as np
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from app import db
from app.models import UploadBatch, FuelPrice
from dateutil import parser as date_parser

# Blueprint for modular route handling
fuel_upload_bp = Blueprint('fuel_upload', __name__)

# Get app context
from app import db

# Ensure uploads folder exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Route to handle CSV upload
@fuel_upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == "" or not allowed_file(file.filename):
        return jsonify(error="Please upload a valid .csv file"), 400

    filename = secure_filename(file.filename)
    unique_prefix = f"{current_user.id}_{secrets.token_hex(8)}"
    saved_name = f"{unique_prefix}_{filename}"
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, saved_name)
    file.save(filepath)

    batch = UploadBatch(
        user_id=current_user.id,
        filename=filename,
        uploaded_at=datetime.utcnow()
    )
    db.session.add(batch)

    try:
        df = pd.read_csv(filepath, dtype=str)

        for _, row in df.iterrows():
            raw_date = row.get('PUBLISH_DATE', '').strip()
            price_date = None
            if raw_date:
                if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', raw_date):
                    try:
                        price_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
                    except ValueError:
                        price_date = None

                if price_date is None:
                    try:
                        price_date = date_parser.parse(raw_date, dayfirst=False).date()
                    except (ValueError, OverflowError):
                        price_date = None

                if price_date is None:
                    price_date = batch.uploaded_at.date()

            entry = FuelPrice(
                batch=batch,
                publish_date=price_date,
                trading_name=row.get('TRADING_NAME'),
                brand_description=row.get('BRAND_DESCRIPTION'),
                product_description=row.get('PRODUCT_DESCRIPTION'),
                product_price=float(row.get('PRODUCT_PRICE', 0)) if row.get('PRODUCT_PRICE') else None,
                address=row.get('ADDRESS'),
                location=row.get('LOCATION'),
                postcode=row.get('POSTCODE'),
                area_description=row.get('AREA_DESCRIPTION'),
                region_description=row.get('REGION_DESCRIPTION')
            )
            db.session.add(entry)

        db.session.commit()
        try:
            df = pd.read_csv(filepath)

            sample_df = df.head(5).replace({np.nan: None})
            sample_df = sample_df.iloc[:, 0:6]
            sample = sample_df.to_dict(orient="records")

            return jsonify(
            message="File uploaded and data saved successfully.",
            sample=sample
            ), 200
        except Exception as e:
            return jsonify(error=str(e)), 500

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to process uploaded CSV")
        return jsonify(error=str(e)), 500