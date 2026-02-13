
from datetime import datetime
from flask_pymongo import ObjectId

class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "created_at": self.created_at
        }

class Tracker:
    def __init__(self, user_id, title, pixel_id, client_id=None):
        self.user_id = ObjectId(user_id) if user_id else None
        self.client_id = client_id
        self.title = title
        self.pixel_id = pixel_id
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "client_id": self.client_id,
            "title": self.title,
            "pixel_id": self.pixel_id,
            "created_at": self.created_at
        }

class OpenEvent:
    def __init__(self, tracker_id, ip_address, user_agent, country=None, device_type=None):
        self.tracker_id = ObjectId(tracker_id)
        self.timestamp = datetime.utcnow()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.country = country
        self.device_type = device_type

    def to_dict(self):
        return {
            "tracker_id": self.tracker_id,
            "timestamp": self.timestamp,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "country": self.country,
            "device_type": self.device_type
        }
