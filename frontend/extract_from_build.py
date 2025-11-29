#!/usr/bin/env python3
import zipfile
import os
import shutil

# Path to the existing build.zip on the server
build_zip_path = "/home/blindflugstudios/CharacterEditor/build.zip"
static_path = "/home/blindflugstudios/CharacterEditor/static"

if os.path.exists(build_zip_path):
    print(f"Found build.zip at {build_zip_path}")
    with zipfile.ZipFile(build_zip_path, 'r') as zip_ref:
        # Extract only PortraitSprites folder
        for file_info in zip_ref.infolist():
            if file_info.filename.startswith('build/PortraitSprites/'):
                # Remove 'build/' prefix when extracting
                target_path = file_info.filename.replace('build/', '', 1)
                target_full_path = os.path.join(static_path, target_path)
                
                if file_info.is_dir():
                    os.makedirs(target_full_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_full_path), exist_ok=True)
                    with zip_ref.open(file_info) as source, open(target_full_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    print(f"✓ Extracted {target_path}")
    print("Extraction complete!")
else:
    print(f"build.zip not found at {build_zip_path}")
    print("Please upload build.zip first")
