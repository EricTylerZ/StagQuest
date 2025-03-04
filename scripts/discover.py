# scripts/discover.py
import os
import json
from flask import Flask, jsonify
from werkzeug.serving import run_simple

app = Flask(__name__)

# Absolute path to data directory
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

@app.route('/stags', methods=['GET'])
def get_all_stags():
    """Return a JSON list of all stags from users.json with user_id, token_id, day, and days_completed."""
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        
        all_stags = []
        for user_id, data in users.items():
            stag_info = {
                'user_id': user_id,
                'token_id': data['token_id'],
                'day': data['day'],
                'days_completed': data.get('days_completed', 0)  # Fallback to 0 if not present
            }
            all_stags.append(stag_info)
        
        return jsonify(all_stags), 200
    except FileNotFoundError:
        return jsonify({'error': 'users.json not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_app():
    """Run the Flask app with reloader disabled for production readiness."""
    run_simple('0.0.0.0', 5000, app, use_reloader=False)

if __name__ == '__main__':
    run_app()