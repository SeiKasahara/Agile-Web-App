from flask import Blueprint, jsonify, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.models import db, User
import os
from app.utils.mail import send_reset_email
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)

auth_bp = Blueprint("auth", __name__,template_folder="../../templates/main")
env = os.getenv('FLASK_ENV', 'development')

def generate_reset_token(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user.id})

def verify_reset_token(token, expires_sec=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, max_age=expires_sec)
        return User.query.get(data.get('user_id'))
    except (SignatureExpired, BadSignature):
        return None

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_home"))
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        verified = False

        if User.query.filter_by(email=email).first():
            return jsonify({"status": "fail", "message": "Email already registered"}), 400

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=f"{first_name} {last_name}",
            email=email,
            verified=verified,
            is_social_login=False
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            return jsonify({"status": "success", "message": "Account created"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": "Server error"}), 500

    return render_template("main/signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({"status": "success", "message": "Login Success"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid email or password!"}), 400

    return render_template("main/login.html")

@auth_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()

    if not user_info or 'email' not in user_info:
        return jsonify({"status": "error", "message": "Google login failed"}), 400

    email = user_info['email']
    full_name = user_info.get('name', '')
    first_name = user_info.get('given_name', '')
    last_name = user_info.get('family_name', '')

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            email=email,
            username=full_name,
            first_name=first_name,
            last_name=last_name,
            verified=True,
            is_social_login=True
        )
        user.set_password("Google"+full_name)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.set_password"))
    login_user(user)
    return redirect(url_for("dashboard.dashboard_home"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    user = verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("auth.login"))
    user.verified = True
    db.session.commit()
    flash("Email verified successfully. You can now log in.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/set-password", methods=["GET", "POST"])
@login_required
def set_password():
    if request.method == "POST":
        new_password = request.form.get("new_password")
        current_user.set_password(new_password)
        try:
            db.session.commit()
            return jsonify({"status": "success", "message": "Password set successfully."}), 200
        except Exception:
            db.session.rollback()
            return jsonify({"status": "error", "message": "Server error"}), 500

    return render_template("main/reset_password.html", title="Set Password")

@auth_bp.route("/reset-password-demo")
def reset_password_demo():
    demo_user = User.query.first()
    token = generate_reset_token(demo_user)
    return redirect(url_for("auth.reset_password", token=token))

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.form.get("email")

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        token = generate_reset_token(user)
        reset_link = url_for('auth.reset_password', token=token, _external=True)
        try:
            send_reset_email(user.email, reset_link)
            return jsonify({"status": "success", "message": "A reset link has been sent."}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": "Failed to send email."}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid email!"}), 400


if env == "development":
    @auth_bp.route("/reset-password-demo")
    def reset_password_demo():
        demo_user = User.query.first()
        token = generate_reset_token(demo_user)
        return redirect(url_for("auth.reset_password", token=token))

