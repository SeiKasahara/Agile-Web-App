import os
import pandas as pd
from flask import current_app
from app import db
from app.models import Station

def load_wa_stations():
    csv_path = os.path.join(current_app.root_path, 'geodata', 'geodata_db.csv')
    if not os.path.exists(csv_path):
        current_app.logger.warning(f"WA stations CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path, dtype=str).fillna('')
    inserted = 0

    for _, row in df.iterrows():
        addr = row['ADDRESS'].strip()
        post = row['POSTCODE'].strip()

        exists = Station.query.filter_by(address=addr, postcode=post).first()
        if exists:
            continue

        st = Station(
            name   = row['TRADING_NAME'].strip(),
            address        = addr,
            suburb         = row['LOCATION'].strip(),
            postcode       = post,
            area           = row['AREA_DESCRIPTION'].strip(),
            region         = row['REGION_DESCRIPTION'].strip(),
            latitude       = float(row['latitude']),
            longitude      = float(row['longitude'])
        )
        db.session.add(st)
        inserted += 1

    if inserted:
        db.session.commit()
        current_app.logger.info(f"Loaded {inserted} new WA stations from CSV")
    else:
        db.session.rollback()