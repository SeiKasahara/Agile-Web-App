from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # ...
        return redirect(url_for("auth.signup"))  # redirect elsewhere
    return render_template("main/signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # ...
        return redirect(url_for("auth.login"))  # redirect elsewhere
    return render_template("main/login.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        # ...
        return redirect(url_for("auth.login"))  # redirect elsewhere
    return render_template("main/reset_password.html", token=token)

# Please remove this on product environment.
@auth_bp.route("/reset-password-demo")
def reset_password_demo():
    return render_template("main/reset_password.html", token="demo-token")
