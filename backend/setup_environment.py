#!/usr/bin/env python3
"""
Setup virtual environment and install dependencies on PythonAnywhere
"""
import requests
import time
import sys

USERNAME = 'blindflugstudios'
API_TOKEN = '11303eb0a2611d2a49345f01c5c4760f30a4c4f5'
BASE_URL = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}'
PROJECT_DIR = f'/home/{USERNAME}/crew-generator-backend'

headers = {'Authorization': f'Token {API_TOKEN}'}

def create_console():
    """Create a new console"""
    url = f'{BASE_URL}/consoles/'
    response = requests.post(url, headers=headers)

    if response.status_code == 201:
        console_id = response.json()['id']
        print(f'✓ Created console: {console_id}')
        return console_id
    else:
        print(f'✗ Failed to create console: {response.status_code}')
        print(response.text)
        return None

def send_input(console_id, command):
    """Send input to console"""
    url = f'{BASE_URL}/consoles/{console_id}/send_input/'
    response = requests.post(
        url,
        headers=headers,
        json={'input': command + '\n'}
    )

    if response.status_code == 200:
        print(f'✓ Sent: {command}')
        return True
    else:
        print(f'✗ Failed: {response.status_code}')
        return False

def get_console_output(console_id):
    """Get latest console output"""
    url = f'{BASE_URL}/consoles/{console_id}/get_latest_output/'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        output = response.json().get('output', '')
        return output
    return ''

def main():
    print('='*60)
    print('Setting up Python environment on PythonAnywhere')
    print('='*60)
    print()

    # Create console
    print('Creating console...')
    console_id = create_console()

    if not console_id:
        print('Failed to create console')
        sys.exit(1)

    time.sleep(2)

    # Commands to run
    commands = [
        f'cd {PROJECT_DIR}',
        'python3.10 -m venv venv',
        'source venv/bin/activate',
        'pip install --upgrade pip',
        'pip install -r requirements.txt',
        'python manage.py migrate',
        'python manage.py collectstatic --noinput',
        'echo "Setup complete!"'
    ]

    print('\nRunning setup commands...')
    for cmd in commands:
        print(f'\n→ {cmd}')
        send_input(console_id, cmd)
        time.sleep(3)  # Wait for command to execute

        # Get output
        output = get_console_output(console_id)
        if output:
            print(output[-500:])  # Print last 500 chars

    print('\n' + '='*60)
    print('Environment setup complete!')
    print('='*60)

if __name__ == '__main__':
    main()
