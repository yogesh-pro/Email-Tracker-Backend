
from datetime import datetime
from flask_pymongo import ObjectId

class User:
    def __init__(self, email, password_hash=None, google_id=None, is_verified=False, is_premium=False):
        self.email = email
        self.password_hash = password_hash
        self.google_id = google_id
        self.is_verified = is_verified
        self.is_premium = is_premium
        self.otp_code = None
        self.otp_expiry = None
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "google_id": self.google_id,
            "is_verified": self.is_verified,
            "is_premium": self.is_premium,
            "otp_code": self.otp_code,
            "otp_expiry": self.otp_expiry,
            "created_at": self.created_at
        }

class Tracker:
    def __init__(self, user_id, title, pixel_id, client_id=None, recipients=None):
        self.user_id = ObjectId(user_id) if user_id else None
        self.client_id = client_id
        self.title = title
        self.pixel_id = pixel_id
        self.recipients = recipients or []
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "client_id": self.client_id,
            "title": self.title,
            "pixel_id": self.pixel_id,
            "recipients": self.recipients,
            "created_at": self.created_at
        }

class OpenEvent:
    def __init__(self, tracker_id, ip_address, user_agent, device_type=None):
        self.tracker_id = ObjectId(tracker_id)
        self.timestamp = datetime.utcnow()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.device_type = device_type or "Unknown"

    def to_dict(self):
        return {
            "tracker_id": self.tracker_id,
            "timestamp": self.timestamp,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_type": self.device_type
        }
