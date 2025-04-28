from flask import Blueprint, render_template, request, redirect, url_for, current_app,flash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.models import db, User

auth_bp = Blueprint("auth", __name__,template_folder="../../templates/main")

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
        confirm_password = request.form.get("confirm_password")

        if not all([first_name, last_name, email, password, confirm]):
            flash("All fields are required!", "error")
            return redirect(url_for("auth.signup"))

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("auth.signup"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return redirect(url_for("auth.signup"))

        user = User(
            first_name = first_name,
            last_name = last_name,
            username = f"{first_name} {last_name}",
            email=email,
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("auth.login")), 200
        except Exception as e:
            db.session.rollback()
            flash("Error creating account. Please try again.", "error")
            return redirect(url_for("auth.signup")), 500

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
            flash("Login successful!", "success")
            return redirect(url_for("main.index")), 200
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for("auth.login")), 401 # redirect elsewhere

    return render_template("main/login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

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
        confirm = request.form.get("confirm_password")
        if new_password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        user.set_password(new_password)
        db.session.commit()
        flash("Your password has been updated. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("main/reset_password.html", token=token)





# Please remove this on product environment.
@auth_bp.route("/reset-password-demo")
def reset_password_demo():
    demo_user = User.query.first()  # Get the first user in the database
    token = generate_reset_token(demo_user)
    return redirect(url_for("auth.reset_password", token=token))
