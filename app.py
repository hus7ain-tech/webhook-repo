from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv('MONGO_URI')

if not MONGO_URI:
    raise ValueError("MONGO_URI not found. please create .env file based on .env.example.")

client = MongoClient(MONGO_URI)
db = client['techstax_db']
collection = db['github_events']

@app.route('/webhook', methods=['POST'])
def github_webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    if not payload:
        return jsonify({"message": "No payload provided"}), 400

    document = {}

    if event_type == 'push':
        document = {
            "request_id": payload.get('after'),
            "author": payload.get('pusher', {}).get('name', 'Unknown'),
            "action": "PUSH",
            "from_branch": "",
            "to_branch": payload.get('ref', '').split('/')[-1],
            "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
        }

    elif event_type == 'pull_request':
        pr_action = payload.get('action')
        pull_request = payload.get('pull_request', {})

        if pr_action == 'closed' and pull_request.get('merged'):
            document = {
                "request_id": str(pull_request.get('id')),
                "author": pull_request.get('merged_by', {}).get('login', 'Unknown'),
                "action": "MERGE",
                "from_branch": pull_request.get('head', {}).get('ref', ''),
                "to_branch": pull_request.get('base', {}).get('ref', ''),
                "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
            }
        elif pr_action in ['opened', 'reopened', 'synchronize']:
            document = {
                "request_id": str(pull_request.get('id')),
                "author": pull_request.get('user', {}).get('login', 'Unknown'),
                "action": "PULL_REQUEST",
                "from_branch": pull_request.get('head', {}).get('ref', ''),
                "to_branch": pull_request.get('base', {}).get('ref', ''),
                "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
            }


    if document:
        collection.insert_one(document)
        return jsonify({"message": "Event recorded successfully"}), 201

    return jsonify({"message": "Ignored event"}), 200


@app.route('/api/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {"_id": 0}).sort("_id", -1).limit(50))
    return jsonify(events), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)