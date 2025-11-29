#!/usr/bin/env python3
"""
Deploy frontend build to PythonAnywhere
"""
import requests
import os
from pathlib import Path

USERNAME = 'blindflugstudios'
API_TOKEN = '11303eb0a2611d2a49345f01c5c4760f30a4c4f5'
BASE_URL = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}'
PROJECT_DIR = f'/home/{USERNAME}/crew-generator'

headers = {'Authorization': f'Token {API_TOKEN}'}

def create_directory(remote_path):
    """Create a directory on PythonAnywhere"""
    url = f'{BASE_URL}/files/path{remote_path}'
    response = requests.post(url, headers=headers, json={})
    if response.status_code in [200, 201]:
        print(f'✓ Created: {remote_path}')
    return True

def upload_file(local_path, remote_path):
    """Upload a file to PythonAnywhere"""
    url = f'{BASE_URL}/files/path{remote_path}'

    with open(local_path, 'rb') as f:
        content = f.read()

    response = requests.post(url, headers=headers, files={'content': content})

    if response.status_code in [200, 201]:
        print(f'✓ {remote_path}')
        return True
    else:
        print(f'✗ Failed: {remote_path} ({response.status_code})')
        return False

def upload_directory(local_dir, remote_dir):
    """Recursively upload directory"""
    local_dir = Path(local_dir)

    for item in local_dir.rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(local_dir)
            remote_path = f'{remote_dir}/{relative_path}'.replace('\\', '/')

            # Create parent directory
            parent_dir = '/'.join(remote_path.split('/')[:-1])
            create_directory(parent_dir)

            # Upload file
            upload_file(item, remote_path)

def main():
    print('='*60)
    print('Deploying Frontend to PythonAnywhere')
    print('='*60)
    print()

    frontend_build = Path(__file__).parent / 'frontend' / '.svelte-kit' / 'output'

    if not frontend_build.exists():
        print('✗ Build directory not found')
        print('  Run: cd frontend && npm run build')
        return

    print('Step 1: Creating project directories...')
    create_directory(PROJECT_DIR)
    create_directory(f'{PROJECT_DIR}/client')
    create_directory(f'{PROJECT_DIR}/server')
    create_directory(f'{PROJECT_DIR}/static')
    print()

    print('Step 2: Uploading client files...')
    client_dir = frontend_build / 'client'
    if client_dir.exists():
        upload_directory(client_dir, f'{PROJECT_DIR}/client')
    print()

    print('Step 3: Uploading server files...')
    server_dir = frontend_build / 'server'
    if server_dir.exists():
        upload_directory(server_dir, f'{PROJECT_DIR}/server')
    print()

    print('Step 4: Uploading static assets...')
    static_dir = Path(__file__).parent / 'frontend' / 'static'
    if static_dir.exists():
        upload_directory(static_dir, f'{PROJECT_DIR}/static')
    print()

    print('='*60)
    print('Frontend uploaded successfully!')
    print('='*60)

if __name__ == '__main__':
    main()
