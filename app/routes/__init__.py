from .main import main
from .auth import auth_bp

# Function to register routes with the Flask app
def register_routes(app):
    app.register_blueprint(main)  # Register main blueprint
    app.register_blueprint(auth_bp)  # Register auth blueprint