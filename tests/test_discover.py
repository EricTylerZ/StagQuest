# tests/test_discover.py
import os
import json
import sys
from threading import Thread
from time import sleep
import requests

# Add scripts to path (assuming discover.py is in scripts/)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from discover import app, USERS_FILE

# Test data directory
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

def setup_test_data():
    """Create a test users.json with sample data."""
    test_users = {
        'stag-1': {'token_id': 1, 'day': 5, 'days_completed': 4, 'owner': '0x123'},
        'stag-2': {'token_id': 2, 'day': 10, 'days_completed': 9, 'owner': '0x456'},
        'stag-3': {'token_id': 3, 'day': 9, 'days_completed': 8, 'owner': '0x789'}
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(test_users, f)

def run_server():
    """Run the Flask server in a separate thread."""
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def test_get_all_stags():
    """Test the /stags endpoint returns all stags with user_id, token_id, day, and days_completed."""
    # Setup test data
    setup_test_data()

    # Start server in a thread
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Give server time to start
    sleep(1)

    # Hit the endpoint
    response = requests.get('http://localhost:5000/stags')
    data = response.json()

    # Assertions
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert len(data) == 3, f"Expected 3 stags, got {len(data)}"
    assert any(stag['user_id'] == 'stag-1' and stag['token_id'] == 1 and stag['day'] == 5 and stag['days_completed'] == 4 for stag in data), "Stag-1 missing or incorrect"
    assert any(stag['user_id'] == 'stag-2' and stag['token_id'] == 2 and stag['day'] == 10 and stag['days_completed'] == 9 for stag in data), "Stag-2 missing or incorrect"
    assert any(stag['user_id'] == 'stag-3' and stag['token_id'] == 3 and stag['day'] == 9 and stag['days_completed'] == 8 for stag in data), "Stag-3 missing or incorrect"

    print("Test passed: GET /stags returns all stags correctly")

if __name__ == '__main__':
    try:
        test_get_all_stags()
    except Exception as e:
        print(f"Test failed: {str(e)}")
    finally:
        # Clean up test file
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)