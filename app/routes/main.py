from flask import render_template
from flask import Blueprint
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html', title='Home')

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', user=current_user)
