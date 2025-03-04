# tests/test_discover.py
import os
import sys
from threading import Thread
from time import sleep
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from discover import app, PUBLIC_USERS_FILE

def run_server():
    """Run the Flask server in a separate thread."""
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def test_get_all_stags():
    """Test the /stags endpoint returns stags from public_users.json."""
    if not os.path.exists(PUBLIC_USERS_FILE):
        raise FileNotFoundError("public_users.json not found - run sync_public_stags.py first")

    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    sleep(1)

    response = requests.get('http://localhost:5000/stags')
    data = response.json()

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert isinstance(data, list), "Response should be a list"
    assert len(data) > 0, "Expected at least one stag"
    for stag in data:
        assert 'user_id' in stag, "Stag missing user_id"
        assert 'token_id' in stag, "Stag missing token_id"
        assert 'day' in stag, "Stag missing day"
        assert 'days_completed' in stag, "Stag missing days_completed"
        assert 'total_staked' in stag, "Stag missing total_staked"
        assert 'stake_remaining' in stag, "Stag missing stake_remaining"
        assert 'stake_tx' in stag, "Stag missing stake_tx"

    print("Test passed: GET /stags returns all stags correctly")

if __name__ == "__main__":
    try:
        test_get_all_stags()
    except Exception as e:
        print(f"Test failed: {str(e)}")