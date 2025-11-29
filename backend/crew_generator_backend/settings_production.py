"""
Production settings for PythonAnywhere deployment
Import this in settings.py when deploying
"""
import os

# Import all settings from base settings
from .settings import *

# SECURITY WARNING: Update this with a secure secret key in production
# Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Update with your PythonAnywhere username
ALLOWED_HOSTS = [
    'YOUR_USERNAME.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# CORS Configuration for production
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:4173',
    'http://127.0.0.1:5173',
    # Add your production frontend URL here:
    # 'https://your-frontend-domain.com',
]

# Static files configuration for PythonAnywhere
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
