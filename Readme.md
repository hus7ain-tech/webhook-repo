
# TechStaX Assessment: Webhook Receiver (webhook-repo)

## Overview
This repository contains a Python Flask-based webhook receiver designed to capture GitHub events ("Push", "Pull Request", and "Merge") from a designated action repository (`action-repo`). Captured events are parsed and securely logged into a MongoDB database. This application also exposes a RESTful API endpoint for a frontend UI to poll the database and render real-time updates.

## Features
* **Event Listening:** Actively listens to `push` and `pull_request` webhook payloads triggered by GitHub actions.
* **Data Parsing & Formatting:** Extracts relevant information (author, action type, source/target branches, and timestamp) and maps it to the strictly required MongoDB schema.
* **Database Integration:** Securely connects to MongoDB Atlas using environment variables to store all captured event logs.
* **Polling API:** Provides a `/api/events` GET endpoint that serves the latest 50 events in chronological order (newest first) for frontend consumption.
* **Cross-Origin Resource Sharing (CORS):** Enabled to allow frontend applications to fetch data safely without encountering cross-origin network errors.

## Prerequisites
* Python 3.8+
* MongoDB Atlas Account (or a local MongoDB instance)
* `ngrok` (for local development and exposing the Flask server to GitHub)

## Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/hus7ain-tech/webhook-repo.git](https://github.com/hus7ain-tech/webhook-repo.git)
cd webhook-repo
```

### 2.Set Up a Virtual Environment
python -m venv venv
# On Mac/Linux:
source venv/bin/activate  
# On Windows:
venv\Scripts\activate

### 3. Install Dependencies
* pip install -r requirements.txt

### 4.Configure Environment variables
Create a .env file in the root directory of this repository. Add your MongoDB Atlas connection string to securely link the database:
* MONGO_URI="mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority"

### 5. Run the Flask Application
Start the backend server:
* python app.py

**This part is for testing**
### 6. Expore the Server with ngrok
Because GitHub webhooks require a publicly accessible URL, use ngrok to create a secure tunnel to your local server. In a separate terminal window, run:
* ngrok http 5000
Copy the generated HTTPS Forwarding URL (e.g., https://abc1-23-45.ngrok.app).

### Configure github webhooks on the action repo

1. Navigate to your separate action-repo on GitHub.
2. Go to Settings -> Webhooks -> Add webhook.
3. In the Payload URL field, paste your ngrok URL followed by /webhook (e.g., https://abc1-23-45.ngrok.app/webhook).
4. Set the Content type to application/json.
5. Under "Which events would you like to trigger this webhook?", select "Let me select individual events".
6. Check the boxes for Pushes and Pull requests.
7. Click Add webhook to save.

