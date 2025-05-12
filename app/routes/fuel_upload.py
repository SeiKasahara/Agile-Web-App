import io
import re
import os, secrets
from flask import Blueprint, Response, request, jsonify, current_app
from flask_login import login_required, current_user
import numpy as np
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
from app import db
from app.models import FuelType, PriceRecord, Station, UploadBatch
from dateutil import parser as date_parser
from app.utils.geocode import geocode_address

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
    db.session.flush()

    try:
        df = pd.read_csv(filepath, dtype=str).fillna('') 
        station_cache   = {}
        fueltype_cache  = {}

        for _, row in df.iterrows():
            # —— A. Station ——
            addr   = row['ADDRESS'].strip()
            post   = row['POSTCODE'].strip()
            key    = (addr, post)
            if key not in station_cache:
                station = Station.query.filter_by(address=addr, postcode=post).first()
                if not station:
                    lat, lng = geocode_address(row['AREA_DESCRIPTION'], addr)
                    station = Station(
                        name      = row['TRADING_NAME'].strip(),
                        address           = addr,
                        suburb            = row['LOCATION'].strip(),
                        postcode          = post,
                        area              = row['AREA_DESCRIPTION'].strip(),
                        region            = row['REGION_DESCRIPTION'].strip(),
                        latitude          = lat,
                        longitude         = lng
                    )
                    db.session.add(station)
                    db.session.flush() 
                station_cache[key] = station
            station = station_cache[key]

            # —— B. FuelType ——
            ft_name = row['PRODUCT_DESCRIPTION'].strip()
            if ft_name not in fueltype_cache:
                ft = FuelType.query.filter_by(name=ft_name).first()
                if not ft:
                    ft = FuelType(name=ft_name)
                    db.session.add(ft)
                    db.session.flush()
                fueltype_cache[ft_name] = ft
            fuel_type = fueltype_cache[ft_name]

            # —— C. Date ——
            raw = row['PUBLISH_DATE'].strip()
            price_date = None
            if raw:
                if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', raw):
                    try:
                        price_date = datetime.strptime(raw, "%d/%m/%Y").date()
                    except ValueError:
                        price_date = None
                if price_date is None:
                    try:
                        price_date = date_parser.parse(raw, dayfirst=False).date()
                    except Exception:
                        price_date = None
            if price_date is None:
                price_date = batch.uploaded_at.date()

            # —— D. PriceRecord ——
            price = None
            try:
                price = float(row['PRODUCT_PRICE'])
            except ValueError:
                price = None

            rec = PriceRecord(
                station_id   = station.id,
                fuel_type_id = fuel_type.id,
                date         = price_date,
                price        = price,
                batch_id     = batch.id
            )
            db.session.add(rec)
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
    

@fuel_upload_bp.route('/upload/template')
@login_required
def download_template():
    cols = [
        'PUBLISH_DATE','TRADING_NAME','BRAND_DESCRIPTION',
        'PRODUCT_DESCRIPTION','PRODUCT_PRICE','ADDRESS',
        'LOCATION','POSTCODE','AREA_DESCRIPTION','REGION_DESCRIPTION'
    ]
    # 空 DataFrame 只写列头
    df = pd.DataFrame(columns=cols)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition':'attachment; filename="fuel_upload_template.csv"'}
    )