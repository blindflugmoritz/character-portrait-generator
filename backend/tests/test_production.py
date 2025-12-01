#!/usr/bin/env python3
"""
Post-deployment tests - run AFTER uploading to server
Verifies production is working correctly
"""
import sys
import requests
import json
from io import BytesIO
from PIL import Image


PRODUCTION_URL = 'https://blindflugstudios.pythonanywhere.com'


def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🔍 Testing health endpoint...")

    try:
        response = requests.get(f'{PRODUCTION_URL}/api/health', timeout=10)

        if response.status_code != 200:
            print(f"  ❌ Health check failed (HTTP {response.status_code})")
            print(f"     Response: {response.text[:200]}")
            return False

        data = response.json()

        if data['status'] != 'healthy':
            print(f"  ❌ Production is unhealthy")
            print(f"     Issues: {data.get('issues', [])}")
            # Print detailed checks
            for check_type, checks in data.get('checks', {}).items():
                print(f"\n     {check_type}:")
                print(f"       {json.dumps(checks, indent=6)}")
            return False

        print(f"  ✅ Health check passed")
        print(f"     Status: {data['status']}")
        print(f"     All files present: {len(data['checks'].get('files', {}))}")
        print(f"     All imports OK: {len(data['checks'].get('imports', {}))}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Failed to connect to production: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_postcard_generation():
    """Test postcard generation with a real character"""
    print("\n🔍 Testing postcard generation...")

    test_character = {
        "gender": "Male",
        "bodyShapeIndex": 1,
        "colorIndices": {"Skin": 2, "Hair": 3, "Eye": 2, "Accessory": 0},
        "parts": {
            "Body": {"index": 0, "variant": 0},
            "Headshape": {"index": 1, "variant": 0},
            "Ears": {"index": 0, "variant": 0},
            "Hair": {"index": 7, "variant": 0},
            "HairBack": {"index": 7, "variant": 0},
            "Eyes": {"index": 12, "variant": 0},
            "Eyebrows": {"index": 0, "variant": 0},
            "Nose": {"index": 2, "variant": 0},
            "Mouth": {"index": 2, "variant": 0},
            "Beard": {"index": -1, "variant": -1},
            "Moustache": {"index": -1, "variant": -1},
            "AccessoryFace": {"index": -1, "variant": -1},
            "AccessoryHead": {"index": -1, "variant": -1},
            "AccessoryFront": {"index": -1, "variant": -1},
            "DetailUpper": {"index": -1, "variant": -1},
            "DetailLower": {"index": -1, "variant": -1},
            "Blemish": {"index": -1, "variant": -1},
            "Clothes": {"index": 0, "variant": 0},
            "ClothesBack": {"index": 0, "variant": 0},
            "Background": {"index": -1, "variant": -1}
        }
    }

    try:
        response = requests.post(
            f'{PRODUCTION_URL}/api/generate-postcard',
            json={'color': 'blue', 'characters': [test_character]},
            timeout=30
        )

        if response.status_code != 200:
            print(f"  ❌ Postcard generation failed (HTTP {response.status_code})")
            print(f"     Response: {response.text[:500]}")
            return False

        # Verify it's a PNG
        content_type = response.headers.get('Content-Type', '')
        if 'image/png' not in content_type:
            print(f"  ❌ Response is not a PNG (Content-Type: {content_type})")
            return False

        # Verify size
        size = len(response.content)
        if size < 100_000:  # Less than 100KB is suspicious
            print(f"  ❌ Postcard is too small ({size} bytes) - might be corrupted")
            return False

        # Load as image
        img = Image.open(BytesIO(response.content))

        # Verify dimensions
        if img.size != (1024, 614):
            print(f"  ❌ Wrong dimensions: {img.size} (expected 1024x614)")
            return False

        # Check if portrait area has content (not all transparent/white)
        # Portrait should be in top-left area
        portrait_area = img.crop((50, 50, 300, 300))

        # Get pixel data
        pixels = list(portrait_area.getdata())

        # Check for variety of colors (indicates portrait is rendered)
        unique_colors = len(set(pixels))

        if unique_colors < 50:  # If less than 50 unique colors, likely blank
            print(f"  ❌ Portrait area appears blank (only {unique_colors} colors)")
            return False

        print(f"  ✅ Postcard generation passed")
        print(f"     Size: {size:,} bytes (~{size/1024/1024:.1f}MB)")
        print(f"     Dimensions: {img.size}")
        print(f"     Portrait area colors: {unique_colors} (portrait visible)")

        return True

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Failed to connect to production: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_version_endpoint():
    """Test version check endpoint"""
    print("\n🔍 Testing version endpoint...")

    try:
        response = requests.get(f'{PRODUCTION_URL}/api/version-check', timeout=10)

        if response.status_code != 200:
            print(f"  ❌ Version check failed (HTTP {response.status_code})")
            return False

        data = response.json()
        version = data.get('version', 'UNKNOWN')

        print(f"  ✅ Version check passed")
        print(f"     Module version: {version}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Failed to connect to production: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def run_all_tests():
    """Run all post-deployment tests"""
    print("=" * 60)
    print("POST-DEPLOYMENT TESTS (Production)")
    print(f"URL: {PRODUCTION_URL}")
    print("=" * 60)

    tests = [
        test_health_endpoint,
        test_version_endpoint,
        test_postcard_generation,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)

    if all(results):
        print("✅ ALL PRODUCTION TESTS PASSED!")
        print("🎉 Deployment successful!")
        print("=" * 60)
        return True
    else:
        failed_count = sum(1 for r in results if not r)
        print(f"❌ {failed_count}/{len(results)} TESTS FAILED")
        print("⚠️  Production may have issues!")
        print("=" * 60)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
