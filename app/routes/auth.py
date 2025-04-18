from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # ...
        return redirect(url_for("auth.signup"))  # Or redirect elsewhere
    return render_template("main/signup.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # ...
        return redirect(url_for("auth.login"))  # Or redirect elsewhere
    return render_template("main/login.html")