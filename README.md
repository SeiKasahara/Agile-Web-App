# Agile-Web-App

The group project for unit CITS5505 agile web development

## Project Structure

## 📁 Project Directory Overview

### Root Directories

- `.github/` – Contains GitHub Actions workflows and issue templates
- `.vscode/` – VS Code workspace settings and recommended extensions
- `app/` – Main Flask application source code
- `migrations/` – Database migration history managed by Flask-Migrate

---

### Inside `app/`

- `app/routes/` – Application route modules (e.g., auth, dashboard)
- `app/templates/` – HTML templates for Jinja2 rendering
- `app/templates/components/` – Reusable UI components
- `app/frontend/` – Static frontend assets (CSS, JS, images)
- `app/frontend/css/` – CSS stylesheets
- `app/frontend/js/` – JavaScript modules
- `app/frontend/assets/` – Images, icons, or fonts
- `app/utils/` – Utility scripts for data processing or analysis

## Setup and Installation

### Prerequisites
- Python 3.9 or newer
- pip (Python package installer)

### Setting up Virtual Environment

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Make sure your virtual environment is activated
2. Set the Flask environment variables:
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development
   ```
3. Run the development server:
   ```bash
   flask run
   ```

The application will be available at `http://localhost:5000`

For more detailed information about Flask installation and setup, refer to the [official Flask documentation](https://flask.palletsprojects.com/en/stable/installation/#activate-the-environment).

## Members

| UWA ID   |    Name     |                               Github user name |
| :------- | :---------: | ---------------------------------------------: |
| 24386873 | Edward Yuan | [@Seikasahara](https://github.com/Seikasahara) |
| 24146595 | Yechang Wu  |           [@Wycers](https://github.com/wycers) |

## Project Layout

The project follows Flask's recommended layout structure:

```
Agile-Web-App/
├── app/                    # Application package
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── routes/            # Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py       # Authentication routes
│   │   └── main.py       # Main application routes
│   ├── templates/         # HTML templates
│   │   ├── base.html     # Base template
│   │   ├── auth/         # Authentication templates
│   │   └── main/         # Main application templates
│   └── static/           # Static files (CSS, JS, images)
│       ├── css/
│       ├── js/
│       └── images/
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py         # Test modules
├── .venv/                # Python virtual environment
├── config.py             # Configuration settings
├── run.py                # Application entry point
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

### Key Components

- `app/`: The main application package containing all the application code
  - `__init__.py`: Creates the application instance and initializes extensions
  - `models.py`: Defines database models using SQLAlchemy
  - `routes/`: Contains route handlers organized by feature
  - `templates/`: HTML templates using Jinja2 templating
  - `static/`: Static files served directly to clients

- `tests/`: Contains the test suite for the application
  - Uses pytest for testing
  - Includes fixtures and test modules

- Configuration and Setup:
  - `config.py`: Application configuration settings
  - `run.py`: Script to run the development server
  - `requirements.txt`: Lists all Python dependencies
  - `.venv/`: Python virtual environment for dependency isolation
