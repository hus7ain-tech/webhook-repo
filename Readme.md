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
