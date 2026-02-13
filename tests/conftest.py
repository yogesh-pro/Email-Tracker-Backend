
import pytest
from backend.app import create_app
from backend.app.config import Config
from unittest.mock import MagicMock
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestConfig(Config):
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/test_db'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    # Mock Mongo
    app.mongo = MagicMock()
    app.mongo.db = MagicMock()
    
    # We need to patch the mongo object in the app module 
    # OR better yet, we can mock the db calls in the routes directly or rely on the fact 
    # that `mongo.db` is accessed via the extension.
    # However, flask_pymongo extension initializes a client.
    # For unit tests without a real DB, we might need to patch `flask_pymongo.PyMongo` or similar.
    
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
