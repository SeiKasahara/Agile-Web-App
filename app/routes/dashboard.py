from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard', template_folder="../../templates/main")

@dashboard_bp.route('/')
@login_required
def dashboard_home():
    return render_template('main/dashboard.html', user=current_user)