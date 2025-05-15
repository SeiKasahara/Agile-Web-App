# app/routes/share.py
from flask import Blueprint, abort, current_app, json, jsonify, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import FuelType, PriceRecord, SharedReport, Station, User
from app import db
from app.routes.dashboard import _gather_dashboard_data
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime
from app.utils.mail import send_share_dashboard_email
import uuid

share_bp = Blueprint('share', __name__, url_prefix='/share')
share_view_bp = Blueprint('share_view', __name__, url_prefix='/s')

def make_share_token(share_id):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    payload = {
        'share_id': share_id,
    }
    return s.dumps(payload)

@share_bp.route('/create', methods=['POST'])
@login_required
def create_share():
    data = request.get_json()
    selected_components = data.get('components', [])
    
    # Get all data first
    chart_data, metrics = _gather_dashboard_data(
        user_id=current_user.id,
        fuel_type=data['fuel'],
        location=data['loc'],
        filter_date=data['date']
    )

    # Filter data based on selected components
    filtered_data = {}
    if 'metrics' in selected_components:
        filtered_data['metrics'] = metrics
    if 'time_trends' in selected_components:
        filtered_data['chart_data'] = chart_data
    if 'forecast' in selected_components:
        filtered_data['forecast_config'] = data['forecastConfig']
    if 'heatmap' in selected_components:
        filtered_data['heatmap_points'] = data['heatmapPoints']
    if 'fuel_comparison' in selected_components:
        filtered_data['fuel_comparison'] = chart_data

    share = SharedReport(
        user_id=current_user.id,
        fuel_type=data['fuel'],
        location=data['loc'],
        date=data['date'],
        forecast_config=json.dumps(filtered_data.get('forecast_config', {})),
        heatmap_points_json=json.dumps(filtered_data.get('heatmap_points', [])),
        components=json.dumps(selected_components),
        chart_data=json.dumps(filtered_data.get('chart_data', {})),
        metrics=json.dumps(filtered_data.get('metrics', {}))
    )
    
    db.session.add(share)
    db.session.commit()

    # Generate both long and short URLs
    token = make_share_token(share_id=share.id)
    long_url = url_for('share.report', token=token, _external=True)
    short_url = url_for('share_view.short_report', share_id=share.id, _external=True)

    # Send email if provided
    if data.get('email'):
        try:
            send_share_dashboard_email(
                current_app=current_app,
                current_user=current_user,
                to_email=data['email'],
                share_url=short_url
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send share email: {e}")

    return jsonify(url=short_url)

@share_view_bp.route('/<share_id>')
def short_report(share_id):
    try:
        # Validate UUID format
        uuid.UUID(share_id)
        share = SharedReport.query.get_or_404(share_id)
        return render_shared_report(share)
    except ValueError:
        abort(404)

@share_bp.route('/report')
def report():
    token = request.args.get('token')
    
    if not token:
        abort(400)
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except BadSignature:
        return "Invalid link", 403
    
    try:
        # Validate UUID format
        uuid.UUID(data['share_id'])
        share = SharedReport.query.get(data['share_id'])
        if not share:
            abort(404)
    except (ValueError, KeyError):
        abort(404)

    return render_shared_report(share)

def render_shared_report(share):
    components = json.loads(share.components or '[]')
    
    # Load stored data
    chart_data = json.loads(share.chart_data or '{}')
    metrics = json.loads(share.metrics or '{}')
    forecast_config = json.loads(share.forecast_config or '{}')
    heatmap_points = json.loads(share.heatmap_points_json or '[]')

    share_user = User.query.get(share.user_id)

    # Check expiration
    expire_range = getattr(share_user, 'share_expire_range', None) or '7d'
    if expire_range != 'never':
        if expire_range.endswith('d'):
            try:
                days = int(expire_range[:-1])
            except ValueError:
                days = 7
            max_age = days * 24 * 3600
        else:
            max_age = 7 * 24 * 3600
        
        # For short URLs, check creation time
        if share.created_at:
            age = (datetime.utcnow() - share.created_at).total_seconds()
            if age > max_age:
                return "Link expired", 403

    return render_template(
        'share/report.html',
        first_name=share_user.first_name,
        last_name=share_user.last_name,
        chart_data=chart_data,
        metrics=metrics,
        fuel_type=share.fuel_type,
        location=share.location,
        date=share.date,
        forecast_config=forecast_config,
        heatmap_points=heatmap_points,
        components=components
    )