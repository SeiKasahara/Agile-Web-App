from flask import (Blueprint, render_template, redirect, url_for, flash, request)
from flask_login import login_user, logout_user, login_required
from app.models import User
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Email validation
        if '@' not in email or '.' not in email:
            flash('Please use a valid email address for registration', 'error')
            return redirect(url_for('auth.register'))

        user = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user:
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        if email_exists:
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username does not exist. Please <a href="/auth/register" class="alert-link">register</a> first.', 'error')
            return redirect(url_for('auth.login'))
        elif not user.check_password(password):
            flash('Incorrect password', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', title='Login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))