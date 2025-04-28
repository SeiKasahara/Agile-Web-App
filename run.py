import os
from dotenv import load_dotenv

from app import create_app

env = os.getenv('FLASK_ENV', 'development')

if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')

app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
