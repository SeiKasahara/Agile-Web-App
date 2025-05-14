from flask import flash, redirect, url_for, render_template, request, jsonify
from flask_wtf.csrf import CSRFError

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Handle CSRF errors."""
        if request.content_type == 'application/json':
            return jsonify(error="CSRF validation failed"), 400
        else:
            flash('The form has expired. Please try again.', 'danger')
            return redirect(url_for('main.index')) 