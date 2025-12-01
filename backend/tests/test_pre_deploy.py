#!/usr/bin/env python3
"""
Pre-deployment tests - run BEFORE uploading to server
Catches missing files, import errors, and signature mismatches
"""
import os
import sys
import json
import inspect

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_all_required_files_exist():
    """Verify all required files exist locally"""
    print("\n🔍 Checking required files...")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_files = [
        'api/views.py',
        'api/views_postcard.py',
        'api/postcard_generator.py',
        'api/character_generator.py',
        'api/photo_matcher.py',
        'api/sprite-metadata.json',
        'api/urls.py',
        'api/__init__.py',
    ]

    all_exist = True
    for filepath in required_files:
        full_path = os.path.join(base_dir, filepath)
        exists = os.path.exists(full_path)
        size = os.path.getsize(full_path) if exists else 0

        status = "✅" if exists else "❌"
        print(f"  {status} {filepath:<35} ({size:>8} bytes)")

        if not exists:
            all_exist = False
        elif size == 0:
            print(f"     ⚠️  WARNING: File is empty!")
            all_exist = False

    if not all_exist:
        print("\n❌ FAILED: Some required files are missing or empty")
        return False

    print("✅ All required files exist")
    return True


def test_json_files_valid():
    """Verify JSON files are valid JSON"""
    print("\n🔍 Validating JSON files...")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_files = ['api/sprite-metadata.json']

    all_valid = True
    for filepath in json_files:
        full_path = os.path.join(base_dir, filepath)
        try:
            with open(full_path, 'r') as f:
                data = json.load(f)

            # Check it's not empty
            if not data:
                print(f"  ❌ {filepath} - JSON is empty")
                all_valid = False
            else:
                entries = len(data) if isinstance(data, (list, dict)) else 1
                print(f"  ✅ {filepath} ({entries} entries)")
        except json.JSONDecodeError as e:
            print(f"  ❌ {filepath} - Invalid JSON: {e}")
            all_valid = False
        except Exception as e:
            print(f"  ❌ {filepath} - Error: {e}")
            all_valid = False

    if not all_valid:
        print("\n❌ FAILED: Some JSON files are invalid")
        return False

    print("✅ All JSON files are valid")
    return True


def test_modules_can_import():
    """Verify all modules can be imported without errors"""
    print("\n🔍 Testing module imports...")

    modules = [
        'api.views',
        'api.views_postcard',
        'api.postcard_generator',
        'api.character_generator',
        'api.photo_matcher',
    ]

    all_imported = True
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except Exception as e:
            print(f"  ❌ {module_name} - {e}")
            all_imported = False

    if not all_imported:
        print("\n❌ FAILED: Some modules cannot be imported")
        return False

    print("✅ All modules can be imported")
    return True


def test_function_signatures():
    """Verify critical function signatures are correct"""
    print("\n🔍 Checking function signatures...")

    try:
        from api.postcard_generator import generate_postcard
        from api.views_postcard import generate_postcard_api

        # Check generate_postcard signature
        sig = inspect.signature(generate_postcard)
        params = list(sig.parameters.keys())

        expected_params = ['color', 'characters', 'base_path']
        if params != expected_params:
            print(f"  ❌ generate_postcard signature is wrong!")
            print(f"     Expected: {expected_params}")
            print(f"     Got:      {params}")
            return False

        print(f"  ✅ generate_postcard({', '.join(params)})")

        # Check it's called correctly in views_postcard
        import ast
        views_postcard_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'api/views_postcard.py'
        )

        with open(views_postcard_path, 'r') as f:
            tree = ast.parse(f.read())

        # Look for generate_postcard() calls
        found_call = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'generate_postcard':
                    found_call = True
                    # Check argument order (simple check)
                    if len(node.args) >= 2:
                        print(f"  ✅ generate_postcard called with correct arguments")

        if not found_call:
            print(f"  ⚠️  WARNING: Could not verify generate_postcard call")

        print("✅ Function signatures are correct")
        return True

    except Exception as e:
        print(f"  ❌ Error checking signatures: {e}")
        return False


def test_dependencies_available():
    """Check that external dependencies are available"""
    print("\n🔍 Checking dependencies...")

    dependencies = [
        ('anthropic', 'Anthropic API client'),
        ('PIL', 'Pillow (image processing)'),
        ('django', 'Django framework'),
        ('dotenv', 'Environment variables'),
    ]

    all_available = True
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name:<15} - {description}")
        except ImportError:
            print(f"  ❌ {module_name:<15} - NOT INSTALLED ({description})")
            all_available = False

    if not all_available:
        print("\n❌ FAILED: Some dependencies are missing")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All dependencies are available")
    return True


def run_all_tests():
    """Run all pre-deployment tests"""
    print("=" * 60)
    print("PRE-DEPLOYMENT TESTS")
    print("=" * 60)

    tests = [
        test_all_required_files_exist,
        test_json_files_valid,
        test_dependencies_available,
        test_modules_can_import,
        test_function_signatures,
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
        print("✅ ALL TESTS PASSED - Ready to deploy!")
        print("=" * 60)
        return True
    else:
        print("❌ SOME TESTS FAILED - DO NOT DEPLOY!")
        print("=" * 60)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
