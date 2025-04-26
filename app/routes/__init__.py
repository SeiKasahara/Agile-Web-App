from flask import Blueprint

from .auth import auth_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
