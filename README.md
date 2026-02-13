
# Email Tracker Backend

Flask-based backend for the Email Tracking System.

## Architecture
- **Framework**: Flask
- **Database**: MongoDB (via `flask_pymongo`)
- **Authentication**: JWT (`flask_jwt_extended`)
- **Tracking**: 1x1 Transparent Pixel
- **Rate Limiting**: `Flask-Limiter`

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment:
   Copy `.env.example` to `.env` and set your MongoDB URI.
   ```bash
   cp .env.example .env
   ```

4. Run the server:
   ```bash
   python run.py
   ```

## Testing

Run unit tests:

```bash
pip install pytest pytest-mock
PYTHONPATH=. pytest backend/tests/test_api.py
```

## API Endpoints

- **POST /api/auth/register**: Register a new user
- **POST /api/auth/login**: Login and get JWT token
- **POST /api/tracker/**: Create a new tracker (requires auth)
- **GET /api/tracker/**: List all trackers (requires auth)
- **DELETE /api/tracker/<id>**: Delete a tracker (requires auth)
- **GET /api/pixel/<id>.png**: The tracking pixel
- **GET /api/analytics/<tracker_id>**: Get analytics for a tracker (requires auth)
