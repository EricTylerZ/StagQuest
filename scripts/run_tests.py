# scripts/run_tests.py
import os
import sys
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEST_DIR = os.path.join(PROJECT_ROOT, 'tests')
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

def setup_environment():
    """Install project dependencies from requirements.txt."""
    print("Setting up environment...")
    subprocess.check_call(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed.")

def sync_stags():
    """Run sync_stags.py to update users.json with real blockchain data."""
    print("Syncing stags from blockchain...")
    sync_script = os.path.join(SCRIPTS_DIR, 'sync_stags.py')
    result = subprocess.run(
        ["python", sync_script],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, "sync_stags.py")
    print("Stags synced successfully!")

def run_tests():
    """Run all tests in the tests directory."""
    print("Running tests...")
    sys.path.insert(0, PROJECT_ROOT)
    test_file = os.path.join(TEST_DIR, 'test_discover.py')
    result = subprocess.run(
        ["python", test_file],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, "test_discover.py")
    print("All tests passed!")

if __name__ == "__main__":
    try:
        setup_environment()
        sync_stags()  # Add this step
        run_tests()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)