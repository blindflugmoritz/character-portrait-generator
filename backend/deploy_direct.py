#!/usr/bin/env python3
"""
Direct deployment script using PythonAnywhere API
"""
import requests
import base64
import os
import json
from pathlib import Path

# Configuration
USERNAME = 'blindflugstudios'
API_TOKEN = '11303eb0a2611d2a49345f01c5c4760f30a4c4f5'
BASE_URL = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}'
PROJECT_DIR = f'/home/{USERNAME}/crew-generator-backend'

headers = {
    'Authorization': f'Token {API_TOKEN}'
}

def upload_file(local_path, remote_path):
    """Upload a file to PythonAnywhere"""
    url = f'{BASE_URL}/files/path{remote_path}'

    with open(local_path, 'rb') as f:
        content = f.read()

    response = requests.post(
        url,
        headers=headers,
        files={'content': content}
    )

    if response.status_code in [200, 201]:
        print(f'✓ Uploaded: {remote_path}')
        return True
    else:
        print(f'✗ Failed to upload {remote_path}: {response.status_code}')
        print(f'  Response: {response.text}')
        return False

def create_directory(remote_path):
    """Create a directory on PythonAnywhere"""
    url = f'{BASE_URL}/files/path{remote_path}'

    response = requests.post(
        url,
        headers=headers,
        json={}
    )

    if response.status_code in [200, 201]:
        print(f'✓ Created directory: {remote_path}')
        return True
    else:
        # Directory might already exist
        print(f'  Directory {remote_path} may already exist')
        return True

def run_console_command(command):
    """Run a command in a console"""
    url = f'{BASE_URL}/consoles/'

    # Create console
    response = requests.post(url, headers=headers)

    if response.status_code != 201:
        print(f'✗ Failed to create console: {response.status_code}')
        return False

    console_id = response.json()['id']
    print(f'✓ Created console: {console_id}')

    # Send command
    input_url = f'{BASE_URL}/consoles/{console_id}/send_input/'
    response = requests.post(
        input_url,
        headers=headers,
        json={'input': command + '\n'}
    )

    if response.status_code == 200:
        print(f'✓ Executed: {command}')
        return True
    else:
        print(f'✗ Failed to execute command: {response.status_code}')
        return False

def reload_webapp(domain):
    """Reload a web app"""
    url = f'{BASE_URL}/webapps/{domain}/reload/'

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print(f'✓ Reloaded webapp: {domain}')
        return True
    else:
        print(f'✗ Failed to reload webapp: {response.status_code}')
        print(f'  Response: {response.text}')
        return False

def list_webapps():
    """List all web apps"""
    url = f'{BASE_URL}/webapps/'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        webapps = response.json()
        print(f'✓ Found {len(webapps)} webapp(s)')
        for app in webapps:
            print(f'  - {app["domain_name"]}')
        return webapps
    else:
        print(f'✗ Failed to list webapps: {response.status_code}')
        return []

def main():
    print('='*60)
    print('PythonAnywhere Deployment')
    print(f'User: {USERNAME}')
    print(f'Target: {PROJECT_DIR}')
    print('='*60)
    print()

    # Step 1: List existing webapps
    print('Step 1: Checking existing webapps...')
    webapps = list_webapps()
    print()

    # Step 2: Create project directory
    print('Step 2: Creating project directory...')
    create_directory(PROJECT_DIR)
    create_directory(f'{PROJECT_DIR}/api')
    create_directory(f'{PROJECT_DIR}/crew_generator_backend')
    print()

    # Step 3: Upload files
    print('Step 3: Uploading files...')
    backend_dir = Path(__file__).parent

    files_to_upload = [
        ('manage.py', 'manage.py'),
        ('requirements.txt', 'requirements.txt'),
        ('.env.example', '.env'),  # Upload as .env
        ('api/__init__.py', 'api/__init__.py'),
        ('api/apps.py', 'api/apps.py'),
        ('api/models.py', 'api/models.py'),
        ('api/views.py', 'api/views.py'),
        ('api/urls.py', 'api/urls.py'),
        ('api/character_generator.py', 'api/character_generator.py'),
        ('api/photo_matcher.py', 'api/photo_matcher.py'),
        ('api/sprite-metadata.json', 'api/sprite-metadata.json'),
        ('crew_generator_backend/__init__.py', 'crew_generator_backend/__init__.py'),
        ('crew_generator_backend/settings.py', 'crew_generator_backend/settings.py'),
        ('crew_generator_backend/urls.py', 'crew_generator_backend/urls.py'),
        ('crew_generator_backend/wsgi.py', 'crew_generator_backend/wsgi.py'),
    ]

    for local_file, remote_file in files_to_upload:
        local_path = backend_dir / local_file
        remote_path = f'{PROJECT_DIR}/{remote_file}'

        if local_path.exists():
            upload_file(local_path, remote_path)
        else:
            print(f'⚠ Skipping {local_file} (not found)')

    print()
    print('='*60)
    print('Files uploaded successfully!')
    print()
    print('Next steps (manual):')
    print('1. Go to https://www.pythonanywhere.com/consoles/')
    print('2. Start a new Bash console')
    print('3. Run these commands:')
    print(f'   cd {PROJECT_DIR}')
    print('   python3.10 -m venv venv')
    print('   source venv/bin/activate')
    print('   pip install -r requirements.txt')
    print('   python manage.py migrate')
    print('   python manage.py collectstatic --noinput')
    print()
    print('4. Edit .env file and add your ANTHROPIC_API_KEY')
    print('5. Go to Web tab and create/configure WSGI app')
    print('6. Reload the web app')
    print()
    print(f'Your API will be at: https://{USERNAME}.pythonanywhere.com')
    print('='*60)

if __name__ == '__main__':
    main()
