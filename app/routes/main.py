from flask import (Blueprint, render_template)
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/index.html', title='Home')

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', title='Profile')
