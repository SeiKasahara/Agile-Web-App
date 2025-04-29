from flask import Blueprint, jsonify, render_template, request, redirect, url_for, current_app,flash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.models import db, User
import os
from app.utils.mail import send_reset_email 

auth_bp = Blueprint("auth", __name__,template_folder="../../templates/main")
env = os.getenv('FLASK_ENV', 'development')

def generate_reset_token(user):
    """
    Generate a reset token for the user.
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user.id})

def verify_reset_token(token, expires_sec=3600):
    """
    Generate a reset token for the user with an expiration time.
    Verify the reset token and return the corresponding user.
    If the verification fails, return None.
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, max_age=expires_sec)
        return User.query.get(data.get('user_id'))
    except (SignatureExpired, BadSignature):
        return None

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        verified = False

        if User.query.filter_by(email=email).first():
            return jsonify({"status": "fail", "message": "Email already registered"}), 400

        user = User(
            first_name = first_name,
            last_name = last_name,
            username = f"{first_name} {last_name}",
            email=email,
            verified=verified
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
        return redirect(url_for("main.index"))

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

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        user.set_password(new_password)
        try:
            db.session.commit()
            return jsonify({"status": "success", "message": "Your password has been updated. Please log in."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": "Server error"}), 500

    return render_template("main/reset_password.html", token=token)

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
            if env == "development":
                return jsonify({"status": "success", "message": "A reset link has been sent."}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": "Failed to send email."}), 500
    else:
        if env == "production":
        # Prevent brute-force email check 
            return jsonify({"status": "success", "message": "If the email exists, a reset link has been sent."}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid email!"}), 400


# Please remove this on product environment.

if env == "development":
    @auth_bp.route("/reset-password-demo")
    def reset_password_demo():
        demo_user = User.query.first()  # Get the first user in the database
        token = generate_reset_token(demo_user)
        return redirect(url_for("auth.reset_password", token=token))
