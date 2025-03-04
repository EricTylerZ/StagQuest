# scripts/discover.py
import os
import json
import sys
from flask import Flask, jsonify
from werkzeug.serving import run_simple

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
PUBLIC_USERS_FILE = os.path.join(DATA_DIR, 'public_users.json')

@app.route('/stags', methods=['GET'])
def get_all_stags():
    """Return a JSON list of all stags from public_users.json."""
    try:
        with open(PUBLIC_USERS_FILE, 'r') as f:
            users = json.load(f)
        all_stags = list(users.values())
        return jsonify(all_stags), 200
    except FileNotFoundError:
        return jsonify({'error': 'public_users.json not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_app():
    """Run the Flask app with reloader disabled."""
    try:
        run_simple('0.0.0.0', 5000, app, use_reloader=False)
    except KeyboardInterrupt:
        print("Shutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    run_app()