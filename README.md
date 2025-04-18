# Agile-Web-App

The group project for unit CITS5505 agile web development

## Project Structure

### 📁 Project Directory Overview

```
Agile-Web-App/
├── app/                    # Main Flask application
│   ├── __init__.py        # Application factory
│   ├── models.py          # Database models
│   ├── routes/            # Route handlers
│   │   ├── __init__.py
│   │   └── main.py       # Main application routes
│   ├── templates/         # HTML templates
│   │   ├── base.html     # Base template
│   │   └── main/         # Main application templates
│   │       └── index.html
│   └── static/           # Static files
│       └── css/
│           └── style.css
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_main.py      # Tests for main routes
├── .github/              # GitHub configuration
├── .vscode/             # VS Code settings
├── .venv/               # Python virtual environment
├── config.py            # Application configuration
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

### Key Directories and Files

#### Application Code (`app/`)
- `__init__.py`: Creates and configures the Flask application
- `models.py`: Database models (currently empty)
- `routes/`: Contains all route handlers
  - `main.py`: Handles main application routes
- `templates/`: HTML templates using Jinja2
  - `base.html`: Base template with common layout
  - `main/`: Templates for main application pages
- `static/`: Static assets (CSS, JS, images)
  - `css/`: Stylesheets
    - `style.css`: Main application styles

#### Testing (`tests/`)
- `test_main.py`: Unit tests for main application routes
- `__init__.py`: Makes tests a Python package

#### Configuration
- `config.py`: Application configuration settings
- `requirements.txt`: Python package dependencies
- `run.py`: Entry point for running the application

#### Development Tools
- `.github/`: GitHub Actions workflows and templates
- `.vscode/`: VS Code workspace settings
- `.venv/`: Python virtual environment

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

You can run the application in two ways:

1. Using Flask CLI:
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development
   flask run
   ```

2. Using Python directly:
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

### Running Tests

To run the test suite:
```bash
pytest
```

## Members

| UWA ID   |    Name     |                               Github user name |
| :------- | :---------: | ---------------------------------------------: |
| 24386873 | Edward Yuan | [@Seikasahara](https://github.com/Seikasahara) |
| 24146595 | Yechang Wu  |           [@Wycers](https://github.com/wycers) |

