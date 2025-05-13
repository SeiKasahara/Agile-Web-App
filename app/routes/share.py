# app/routes/share.py
from flask import Blueprint, abort, current_app, json, jsonify, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import FuelType, PriceRecord, SharedReport, Station
from app import db
from app.routes.dashboard import _gather_dashboard_data
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

share_bp = Blueprint('share', __name__, url_prefix='/share')

def make_share_token(share_id):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    payload = {
        'share_id':   share_id,
    }
    return s.dumps(payload)

@share_bp.route('/create', methods=['POST'])
@login_required
def create_share():
    data = request.get_json()
    
    share = SharedReport(
      user_id             = current_user.id,
      fuel_type           = data['fuel'],
      location            = data['loc'],
      date                = data['date'],
      forecast_config     = json.dumps(data['forecastConfig']),
      heatmap_points_json = json.dumps(data['heatmapPoints'])
    )
    
    db.session.add(share)
    db.session.commit()

    token = make_share_token(share_id=share.id)
    url = url_for('share.report', token=token, _external=True)
    return jsonify(url=url)

@share_bp.route('/report')
@login_required
def report():
    token = request.args.get('token')
    if not token:
        abort(400)
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)
    except SignatureExpired:
        return "Link expired", 403
    except BadSignature:
        return "Invalid link", 403
    
    share = SharedReport.query.get(data['share_id'])
    if not share:
        abort(404)

    chart_data, metrics = _gather_dashboard_data(
        user_id=current_user.id,
        fuel_type=share.fuel_type,
        location=share.location,
        filter_date=share.date
    )

    forecast_config = json.loads(share.forecast_config)
    heatmap_points  = json.loads(share.heatmap_points_json)

    return render_template(
        'share/report.html',
        user                = current_user,
        chart_data    = chart_data,
        metrics       = metrics,
        fuel_type           = share.fuel_type,
        location            = share.location,
        date                = share.date,
        forecast_config     = forecast_config,
        heatmap_points      = heatmap_points
    )