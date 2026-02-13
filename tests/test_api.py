
import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Email Tracker API is running"}

def test_register_user(client):
    with patch('backend.app.routes.auth.mongo') as mock_mongo, \
         patch('backend.app.routes.auth.bcrypt') as mock_bcrypt:
        
        # Setup mock behavior
        mock_mongo.db.users.find_one.return_value = None
        mock_bcrypt.generate_password_hash.return_value = b'hashed_password'
        
        response = client.post('/api/auth/register', json={
            "email": "test@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 201
        assert response.json == {"message": "User created successfully"}
        mock_mongo.db.users.insert_one.assert_called_once()

def test_login_user(client):
    with patch('backend.app.routes.auth.mongo') as mock_mongo, \
         patch('backend.app.routes.auth.bcrypt') as mock_bcrypt:
        
        # Setup mock user
        mock_user = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "password_hash": "hashed_password"
        }
        mock_mongo.db.users.find_one.return_value = mock_user
        mock_bcrypt.check_password_hash.return_value = True
        
        response = client.post('/api/auth/login', json={
            "email": "test@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json

def test_create_tracker(client):
    # Mock authentication first (jwt_required) usually requires valid token
    # or we can mock get_jwt_identity
    
    with patch('backend.app.routes.tracker.get_jwt_identity') as mock_identity, \
         patch('backend.app.routes.tracker.mongo') as mock_mongo, \
         patch('flask_jwt_extended.view_decorators.verify_jwt_in_request'):
        
        mock_identity.return_value = str(ObjectId())
        
        response = client.post('/api/tracker/', json={
            "title": "Test Campaign"
        })
        
        assert response.status_code == 201
        assert "tracking_url" in response.json
        mock_mongo.db.trackers.insert_one.assert_called_once()

def test_track_pixel(client):
    with patch('backend.app.routes.pixel.mongo') as mock_mongo:
        
        # Mock tracker find
        mock_tracker = {"_id": ObjectId(), "user_id": ObjectId()}
        mock_mongo.db.trackers.find_one.return_value = mock_tracker
        
        pixel_id = "some-uuid"
        response = client.get(f'/api/pixel/{pixel_id}.png')
        
        assert response.status_code == 200
        assert response.mimetype == 'image/gif'
        mock_mongo.db.open_events.insert_one.assert_called_once()
