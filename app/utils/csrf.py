from flask import request, current_app
from flask_wtf.csrf import CSRFError
from functools import wraps

def csrf_required(func):
    """
    Decorator to ensure CSRF token is validated for functions that handle
    POST, PUT, PATCH, or DELETE requests.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if not current_app.config.get('WTF_CSRF_ENABLED', True):
                return func(*args, **kwargs)
                
            csrf_token = request.headers.get('X-CSRFToken')
            if not csrf_token:
                csrf_token = request.form.get('csrf_token')
                
            if not csrf_token:
                raise CSRFError('CSRF token missing')
        
        return func(*args, **kwargs)
    return decorated_function 