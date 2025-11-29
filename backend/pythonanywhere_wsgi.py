"""
WSGI configuration for PythonAnywhere deployment

INSTRUCTIONS:
1. Go to PythonAnywhere Web tab
2. Click on WSGI configuration file link
3. Replace the entire contents with this file
4. Update YOUR_USERNAME with your actual PythonAnywhere username
5. Save and reload your web app
"""

import os
import sys

# ======== UPDATE THIS ========
YOUR_USERNAME = 'YOUR_PYTHONANYWHERE_USERNAME'
# =============================

# Add your project directory to the sys.path
path = f'/home/{YOUR_USERNAME}/crew-generator-backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'crew_generator_backend.settings'

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

# Activate virtual environment
activate_this = f'/home/{YOUR_USERNAME}/crew-generator-backend/venv/bin/activate_this.py'
try:
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})
except FileNotFoundError:
    # Python 3.10+ doesn't create activate_this.py
    # The virtual environment will still work without it
    pass

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
