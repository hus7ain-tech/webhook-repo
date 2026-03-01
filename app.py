from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env into the environment

app = Flask(__name__)
# Enable CORS so our frontend can fetch data from this API
CORS(app)

# MongoDB Atlas Connection Setup — loaded from .env
MONGO_URI = os.getenv('MONGO_URI')

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set. Create a .env file based on .env.example.")

client = MongoClient(MONGO_URI)
# This will automatically create the database and collection in Atlas when you insert the first document
db = client['techstax_db']
collection = db['github_events']

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """
    Endpoint to receive GitHub Webhooks[cite: 23].
    """
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    if not payload:
        return jsonify({"message": "No payload provided"}), 400

    document = {}

    # 1. Handle PUSH Event
    if event_type == 'push':
        document = {
            "request_id": payload.get('after'), # Git commit hash [cite: 27]
            "author": payload.get('pusher', {}).get('name', 'Unknown'), # Github user [cite: 27]
            "action": "PUSH", # Enum value [cite: 27]
            "from_branch": "", # LHS branch not typically applicable for standard push
            "to_branch": payload.get('ref', '').split('/')[-1], # RHS branch [cite: 27]
            "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC") # Formatted UTC string [cite: 27]
        }

    # 2. Handle PULL REQUEST & MERGE Events
    elif event_type == 'pull_request':
        pr_action = payload.get('action')
        pull_request = payload.get('pull_request', {})
        
        # Check if it's a MERGE action (Brownie Points) [cite: 13]
        if pr_action == 'closed' and pull_request.get('merged'):
            document = {
                "request_id": str(pull_request.get('id')), # PR ID [cite: 27]
                "author": pull_request.get('merged_by', {}).get('login', 'Unknown'),
                "action": "MERGE",
                "from_branch": pull_request.get('head', {}).get('ref', ''),
                "to_branch": pull_request.get('base', {}).get('ref', ''),
                "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
            }
        # Check if it's a standard PULL_REQUEST opening
        elif pr_action in ['opened', 'reopened', 'synchronize']:
            document = {
                "request_id": str(pull_request.get('id')), # PR ID [cite: 27]
                "author": pull_request.get('user', {}).get('login', 'Unknown'),
                "action": "PULL_REQUEST",
                "from_branch": pull_request.get('head', {}).get('ref', ''),
                "to_branch": pull_request.get('base', {}).get('ref', ''),
                "timestamp": datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
            }

    # Store the data to MongoDB if a valid event was captured [cite: 24]
    if document:
        collection.insert_one(document)
        return jsonify({"message": "Event recorded successfully"}), 201

    return jsonify({"message": "Ignored event"}), 200


@app.route('/api/events', methods=['GET'])
def get_events():
    """
    Endpoint for the UI to poll the latest changes from MongoDB.
    """
    # Fetch the latest 50 events, sorted by newest first
    events = list(collection.find({}, {"_id": 0}).sort("_id", -1).limit(50))
    return jsonify(events), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)