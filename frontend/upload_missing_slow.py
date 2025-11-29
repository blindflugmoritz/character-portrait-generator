import requests
import time
import os

API_TOKEN = "11303eb0a2611d2a49345f01c5c4760f30a4c4f5"
USERNAME = "blindflugstudios"
BASE_URL = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path"

with open('/tmp/missing_files.txt', 'r') as f:
    missing = [line.strip() for line in f]

print(f"Uploading {len(missing)} missing files with 2-second delay between each...")
uploaded = 0
failed = 0

for local_path in missing[:50]:  # Upload first 50 files
    remote_path = f"/home/{USERNAME}/CharacterEditor/static/{local_path}"
    
    try:
        with open(local_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}{remote_path}",
                files={'content': f},
                headers={'Authorization': f'Token {API_TOKEN}'},
                timeout=30
            )
        if response.status_code in [200, 201]:
            uploaded += 1
            if uploaded % 10 == 0:
                print(f"✓ Uploaded {uploaded}/50...")
        else:
            failed += 1
            print(f"✗ {local_path} (HTTP {response.status_code})")
    except Exception as e:
        failed += 1
        print(f"✗ {local_path} ({str(e)})")
    
    time.sleep(2)  # 2 second delay

print(f"\nUploaded: {uploaded}, Failed: {failed}")
