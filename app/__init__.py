from flask import Flask

from app.routes import register_routes

from app.routes.main import main

def create_app():
    app = Flask(__name__)

    register_routes(app)

    app.register_blueprint(main)
    
    return app