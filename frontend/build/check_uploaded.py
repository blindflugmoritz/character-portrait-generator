import requests
import os

API_TOKEN = "11303eb0a2611d2a49345f01c5c4760f30a4c4f5"
USERNAME = "blindflugstudios"
BASE_URL = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path"

missing = []
for root, dirs, files in os.walk("PortraitSprites"):
    for file in files:
        if not file.endswith('.png'):
            continue
        local_path = os.path.join(root, file)
        remote_path = f"/home/{USERNAME}/CharacterEditor/static/{local_path}"
        
        try:
            response = requests.head(
                f"{BASE_URL}{remote_path}",
                headers={'Authorization': f'Token {API_TOKEN}'},
                timeout=5
            )
            if response.status_code != 200:
                missing.append(local_path)
        except:
            missing.append(local_path)

print(f"Total missing: {len(missing)}")
with open('/tmp/missing_files.txt', 'w') as f:
    for path in missing:
        f.write(path + '\n')
