#!/usr/bin/env python3
"""
Complete PythonAnywhere deployment automation
Creates web app and provides final instructions
"""
import requests
import json

USERNAME = 'blindflugstudios'
API_TOKEN = '11303eb0a2611d2a49345f01c5c4760f30a4c4f5'
BASE_URL = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}'
DOMAIN = f'{USERNAME}.pythonanywhere.com'
PROJECT_DIR = f'/home/{USERNAME}/crew-generator-backend'

headers = {'Authorization': f'Token {API_TOKEN}'}

def create_web_app():
    """Create a new web app"""
    url = f'{BASE_URL}/webapps/'

    data = {
        'domain_name': DOMAIN,
        'python_version': 'python310'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f'✓ Created web app: {DOMAIN}')
        return True
    elif response.status_code == 409:
        print(f'  Web app {DOMAIN} already exists')
        return True
    else:
        print(f'✗ Failed to create web app: {response.status_code}')
        print(f'  Response: {response.text}')
        return False

def update_wsgi_file():
    """Update WSGI configuration file"""
    wsgi_path = f'/var/www/{USERNAME}_pythonanywhere_com_wsgi.py'

    wsgi_content = f'''"""
WSGI config for crew-generator-backend project.
"""

import os
import sys

# Add project directory to the sys.path
path = '{PROJECT_DIR}'
if path not in sys.path:
    sys.path.insert(0, path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'crew_generator_backend.settings'

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Activate virtual environment
activate_this = '{PROJECT_DIR}/venv/bin/activate_this.py'
try:
    with open(activate_this) as f:
        exec(f.read(), {{'__file__': activate_this}})
except FileNotFoundError:
    # Python 3.10+ doesn't need activate_this.py
    pass

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''

    url = f'{BASE_URL}/files/path{wsgi_path}'
    response = requests.post(
        url,
        headers=headers,
        files={'content': wsgi_content.encode('utf-8')}
    )

    if response.status_code in [200, 201]:
        print(f'✓ Updated WSGI file')
        return True
    else:
        print(f'✗ Failed to update WSGI: {response.status_code}')
        print(f'  Response: {response.text}')
        return False

def update_settings():
    """Update Django settings for production"""
    settings_path = f'{PROJECT_DIR}/crew_generator_backend/settings.py'

    # Read current settings
    url = f'{BASE_URL}/files/path{settings_path}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f'✗ Failed to read settings: {response.status_code}')
        return False

    settings_content = response.json()['content']

    # Update ALLOWED_HOSTS
    if 'ALLOWED_HOSTS = []' in settings_content:
        settings_content = settings_content.replace(
            'ALLOWED_HOSTS = []',
            f"ALLOWED_HOSTS = ['{DOMAIN}', 'localhost', '127.0.0.1']"
        )

    # Add STATIC_ROOT
    if 'STATIC_ROOT' not in settings_content:
        settings_content = settings_content.replace(
            'STATIC_URL = "static/"',
            f'STATIC_URL = "static/"\nSTATIC_ROOT = os.path.join(BASE_DIR, "static")'
        )

        # Add os import if not present
        if 'import os' not in settings_content:
            settings_content = 'import os\n' + settings_content

    # Upload updated settings
    response = requests.post(
        url,
        headers=headers,
        files={'content': settings_content.encode('utf-8')}
    )

    if response.status_code in [200, 201]:
        print(f'✓ Updated settings.py')
        return True
    else:
        print(f'✗ Failed to update settings: {response.status_code}')
        return False

def configure_static_files():
    """Configure static files mapping"""
    url = f'{BASE_URL}/webapps/{DOMAIN}/static_files/'

    data = {
        'url': '/static/',
        'path': f'{PROJECT_DIR}/static'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print(f'✓ Configured static files')
        return True
    else:
        print(f'  Note: Static files config may need manual setup')
        return False

def reload_webapp():
    """Reload the web app"""
    url = f'{BASE_URL}/webapps/{DOMAIN}/reload/'
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print(f'✓ Reloaded web app')
        return True
    else:
        print(f'✗ Failed to reload: {response.status_code}')
        return False

def main():
    print('='*60)
    print('Complete PythonAnywhere Deployment')
    print('='*60)
    print()

    # Step 1: Create web app
    print('Step 1: Creating web app...')
    create_web_app()
    print()

    # Step 2: Update settings
    print('Step 2: Updating Django settings...')
    update_settings()
    print()

    # Step 3: Update WSGI
    print('Step 3: Configuring WSGI...')
    update_wsgi_file()
    print()

    # Step 4: Configure static files
    print('Step 4: Configuring static files...')
    configure_static_files()
    print()

    print('='*60)
    print('IMPORTANT: Manual Steps Required')
    print('='*60)
    print()
    print('1. Go to https://www.pythonanywhere.com/consoles/')
    print('2. Click "+ Start a new Bash console"')
    print('3. Run these commands:')
    print()
    print(f'   cd {PROJECT_DIR}')
    print('   bash setup.sh')
    print()
    print('4. After setup completes, reload the web app:')
    print(f'   https://www.pythonanywhere.com/#/webapps/{DOMAIN}')
    print()
    print('='*60)
    print('Your API will be available at:')
    print(f'   https://{DOMAIN}/api/')
    print()
    print('Test endpoints:')
    print(f'   - https://{DOMAIN}/api/generate-crew')
    print(f'   - https://{DOMAIN}/api/analyze-photo')
    print('='*60)

if __name__ == '__main__':
    main()
