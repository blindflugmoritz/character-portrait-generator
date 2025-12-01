#!/usr/bin/env python3
"""
Automated deployment script with built-in testing
Ensures safe deployments with pre/post validation
"""
import sys
import os
import subprocess
import time


def run_command(cmd, description, check=True):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")

    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)

    if check and result.returncode != 0:
        print(f"\n❌ FAILED: {description}")
        return False

    print(f"\n✅ SUCCESS: {description}")
    return True


def main():
    """Main deployment workflow"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          AUTOMATED DEPLOYMENT SCRIPT                     ║
║          with Pre/Post Testing                           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    # Step 1: Pre-deployment tests
    print("\n" + "🧪 PHASE 1: PRE-DEPLOYMENT TESTS ".center(60, "="))
    if not run_command(
        'python3 tests/test_pre_deploy.py',
        'Running pre-deployment tests'
    ):
        print("\n" + "="*60)
        print("❌ DEPLOYMENT ABORTED - Pre-deployment tests failed")
        print("="*60)
        print("\nFix the issues above and try again.")
        return False

    # Wait for user confirmation
    print("\n" + "="*60)
    response = input("\n✅ Pre-deployment tests passed. Continue with upload? [y/N]: ")
    if response.lower() != 'y':
        print("\n❌ DEPLOYMENT ABORTED by user")
        return False

    # Step 2: Upload files
    print("\n" + "📤 PHASE 2: UPLOADING FILES ".center(60, "="))

    upload_cmd = """sshpass -p 'HFY.ecy5mem1gcd-nhx' rsync -avz --progress \
        --include='*.py' \
        --include='*.json' \
        --include='*/' \
        --exclude='*' \
        api/ \
        blindflugstudios@ssh.pythonanywhere.com:/home/blindflugstudios/CharacterEditor/api/"""

    if not run_command(upload_cmd, 'Uploading backend files to production'):
        print("\n❌ DEPLOYMENT FAILED - File upload failed")
        return False

    # Step 3: Reload webapp
    print("\n" + "🔄 PHASE 3: RELOADING WEBAPP ".center(60, "="))
    print("Reloading webapp via Python...")

    try:
        # Import here to avoid issues if not available
        import sys
        sys.path.insert(0, '/opt/homebrew/bin')  # Ensure uvx is in path

        # Note: This would need MCP to be available
        # For now, provide instructions
        print("""
To reload the webapp, run:
    mcp__pythonanywhere__reload_webapp with domain: blindflugstudios.pythonanywhere.com

Or manually reload at: https://www.pythonanywhere.com/user/blindflugstudios/webapps/
""")

        input("Press Enter after reloading the webapp...")

    except Exception as e:
        print(f"Note: {e}")
        input("Please reload webapp manually at PythonAnywhere dashboard, then press Enter...")

    # Wait for webapp to restart
    print("\n⏳ Waiting 5 seconds for webapp to restart...")
    time.sleep(5)

    # Step 4: Post-deployment tests
    print("\n" + "🧪 PHASE 4: POST-DEPLOYMENT TESTS ".center(60, "="))
    if not run_command(
        'python3 tests/test_production.py',
        'Running post-deployment tests'
    ):
        print("\n" + "="*60)
        print("⚠️  WARNING: Post-deployment tests failed")
        print("="*60)
        print("\nProduction may have issues. Check the errors above.")
        return False

    # Success!
    print("""

╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          ✅ DEPLOYMENT SUCCESSFUL! 🎉                    ║
║                                                          ║
║  All tests passed!                                       ║
║  Production is healthy and working.                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🌐 Live URL: https://blindflugstudios.pythonanywhere.com
🔍 Health Check: https://blindflugstudios.pythonanywhere.com/api/health

""")
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ DEPLOYMENT ABORTED by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ DEPLOYMENT FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
