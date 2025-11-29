#!/usr/bin/env python3
import os
import requests
from pathlib import Path

API_TOKEN = '11303eb0a2611d2a49345f01c5c4760f30a4c4f5'
USERNAME = 'blindflugstudios'
BASE_URL = 'https://www.pythonanywhere.com/api/v0'

headers = {
    'Authorization': f'Token {API_TOKEN}'
}

# First, delete the old build folder
print("Deleting old build folder...")
response = requests.delete(
    f'{BASE_URL}/user/{USERNAME}/files/path/home/{USERNAME}/build/',
    headers=headers
)
print(f"Delete response: {response.status_code}")

# Upload all files from local build folder
build_dir = Path('../frontend/build')
total_files = sum(1 for _ in build_dir.rglob('*') if _.is_file())
uploaded = 0

for local_path in build_dir.rglob('*'):
    if local_path.is_file():
        relative_path = local_path.relative_to(build_dir)
        remote_path = f'/home/{USERNAME}/build/{relative_path}'

        # Ensure parent directory exists
        parent_dir = str(Path(remote_path).parent)
        requests.post(
            f'{BASE_URL}/user/{USERNAME}/files/path{parent_dir}/',
            headers=headers,
            json={'type': 'directory'}
        )

        # Upload file
        with open(local_path, 'rb') as f:
            response = requests.post(
                f'{BASE_URL}/user/{USERNAME}/files/path{remote_path}',
                headers=headers,
                files={'content': f}
            )

        uploaded += 1
        if uploaded % 10 == 0:
            print(f"Uploaded {uploaded}/{total_files} files...")

print(f"\n✓ Uploaded {uploaded} files!")

# Reload web app
print("\nReloading web app...")
response = requests.post(
    f'{BASE_URL}/user/{USERNAME}/webapps/blindflugstudios.pythonanywhere.com/reload/',
    headers=headers
)
print(f"✓ Reloaded! ({response.status_code})")
