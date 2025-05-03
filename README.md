# Fuel Price Analysis Web App

The group project for unit CITS5505 agile web development

![logo](/app/static/assets/icon.png)

## Project Structure

### 📁 Project Directory Overview

```
Agile-Web-App/
├── app/                    # Main Flask application
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   └── main.py
│   ├── templates/
│   │   ├── base.html
│   │   └── main/
|   |       ├── dashboard.html
|   |       ├── profile.html
│   │       ├── index.html
│   │       ├── login.html
│   │       ├── signup.html
│   │       └── reset_password.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       └── assets/
├── migrations/             # Database migration files
├── tests/                  # Test suite
├── .github/                # GitHub Actions & issue templates
├── .vscode/                # Editor configuration
├── run.py                  # App entry point
├── config.py               # App configuration
├── requirements.txt        # Dependencies
├── .env.development        # Local environment variables
├── .env.production         # Local environment variables
└── README.md               # Project documentation
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

To start the project, use `start.sh`, [dev] means development branch. [prod] means production branch

The application will be available at `http://localhost:5000`

### Running Tests

To run the test suite:

```bash
pytest
```

## Members

| UWA ID   |      Name       |                               Github user name |
| :------- | :-------------: | ---------------------------------------------: |
| 24386873 |   Edward Yuan   | [@Seikasahara](https://github.com/Seikasahara) |
| 24638832 |   Parna Basak   |   [@parnabasak](https://github.com/parnabasak) |
| 24146595 |   Yechang Wu    |           [@Wycers](https://github.com/wycers) |
| 24349497 | Zhengdong Jiang |             [@dgyz8](https://github.com/dgyz8) |
