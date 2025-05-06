from datetime import datetime, timedelta, timezone
import os
import random
import secrets
from werkzeug.utils import secure_filename

from flask import current_app, jsonify, render_template, request, url_for
from flask import Blueprint
from flask_login import login_required, current_user
from app.models import User
from app.utils.mail import send_verification_code
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html', title='Home')

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', user=current_user)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    avatar = request.files.get('avatar')
    if avatar and allowed_file(avatar.filename):
        ext = secure_filename(avatar.filename).rsplit('.', 1)[1].lower()
        fname = f"user_{current_user.id}_{secrets.token_hex(8)}.{ext}"
        avatar_dir = os.path.join(current_app.root_path, 'static', 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)
        path = os.path.join(avatar_dir, fname)
        avatar.save(path)
        current_user.avatar = fname

    first = request.form.get('first_name', '').strip()
    last  = request.form.get('last_name', '').strip()
    if first:
        current_user.first_name = first
    if last:
        current_user.last_name = last

    u = current_user
    u.default_fuel_type  = request.form.get('default_fuel_type', u.default_fuel_type)
    u.default_date_range = request.form.get('default_date_range', u.default_date_range)
    u.default_location   = request.form.get('default_location', u.default_location) or None

    try:
        thr = request.form.get('alert_threshold','').strip()
        u.alert_threshold = float(thr) if thr else None
    except ValueError:
        pass
    u.alert_frequency = request.form.get('alert_frequency', u.alert_frequency)

    u.public_dashboard = True if request.form.get('public_dashboard')=='on' else False

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(status='error', message='Failed to update profile'), 500

    avatar_url = None
    if current_user.avatar:
        avatar_url = url_for('static', filename='avatars/' + current_user.avatar)

    return jsonify(status='success',
                   message='Profile updated',
                   avatar_url=avatar_url), 200

@main.route('/profile/verify-email', methods=['POST'])
@login_required
def verify_email():
    email = request.form.get("email")
    code = f"{random.randint(0, 999999):06d}"
    current_user.email_verify_code = code
    current_user.email_verify_expiration = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()

    try:
        if email:
            if User.query.filter_by(email=email).first():
                return jsonify({"status": "fail", "message": "Email already registered"}), 400
            else:
                send_verification_code(current_app, current_user, email, code)
        else:
            send_verification_code(current_app,current_user, current_user.email, code)
    except Exception:
        return jsonify(status='error', message='Failed to send verification code'), 500

    return jsonify(status='success', message='Verification code sent'), 200


@main.route('/profile/confirm-email', methods=['POST'])
@login_required
def confirm_email():
    data = request.get_json(silent=True) or {}
    code_input = data.get("code", "").strip()
    new_email = data.get("new_email", "")
    if not code_input.isdigit() or len(code_input) != 6:
        return jsonify(status="error", message="Please provide a 6-digit code"), 400

    if not current_user.email_verify_code or not current_user.email_verify_expiration:
        return jsonify(status="error", message="No verification code found. Please request a new one."), 400

    now = datetime.utcnow()
    if now > current_user.email_verify_expiration:
        current_user.email_verify_code = None
        current_user.email_verify_expiration = None
        db.session.commit()
        return jsonify(status="error", message="Verification code has expired. Please request a new one."), 400

    if code_input != current_user.email_verify_code:
        return jsonify(status="error", message="Invalid verification code."), 400
    
    if current_user.email != new_email:
        current_user.email = new_email
    current_user.verified = True
    current_user.email_verify_code = None
    current_user.email_verify_expiration = None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(status="error", message="Server error. Please try again."), 500

    return jsonify(status="success", message="Email verified successfully."), 200