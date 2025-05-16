import os
from dotenv import load_dotenv

from app import create_app

# Get current environment (default to 'development' if not set)
env = os.getenv('FLASK_ENV', 'development')

# Load the appropriate .env file depending on the environment
if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run the app on all available IPs on port 5000 with debug enabled
    app.run(host='0.0.0.0', port=5000, debug=True)
