from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard', template_folder="../../templates/main")

@dashboard_bp.route('/')
@login_required
def dashboard_home():
    # Dummy data for the time trends chart
    chart_data = {
        'daily': {
            'labels': ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            'datasets': [
                {
                    'label': 'ULP',
                    'data': [150, 152, 155, 153, 156, 158],
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                },
                {
                    'label': 'ULP98',
                    'data': [160, 162, 165, 163, 166, 168],
                    'borderColor': 'rgb(255, 99, 132)',
                    'tension': 0.1
                },
                {
                    'label': 'DIESEL',
                    'data': [170, 172, 175, 173, 176, 178],
                    'borderColor': 'rgb(54, 162, 235)',
                    'tension': 0.1
                }
            ]
        },
        'weekly': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'datasets': [
                {
                    'label': 'ULP',
                    'data': [150, 155, 153, 157, 160, 158, 155],
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                },
                {
                    'label': 'ULP98',
                    'data': [160, 165, 163, 167, 170, 168, 165],
                    'borderColor': 'rgb(255, 99, 132)',
                    'tension': 0.1
                },
                {
                    'label': 'DIESEL',
                    'data': [170, 175, 173, 177, 180, 178, 175],
                    'borderColor': 'rgb(54, 162, 235)',
                    'tension': 0.1
                }
            ]
        },
        'monthly': {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'datasets': [
                {
                    'label': 'ULP',
                    'data': [150, 155, 160, 165],
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                },
                {
                    'label': 'ULP98',
                    'data': [160, 165, 170, 175],
                    'borderColor': 'rgb(255, 99, 132)',
                    'tension': 0.1
                },
                {
                    'label': 'DIESEL',
                    'data': [170, 175, 180, 185],
                    'borderColor': 'rgb(54, 162, 235)',
                    'tension': 0.1
                }
            ]
        }
    }
    
    return render_template('main/dashboard.html', user=current_user, chart_data=chart_data)