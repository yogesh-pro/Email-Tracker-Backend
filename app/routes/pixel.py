
from flask import Blueprint, send_file, request
from ..extensions import mongo, limiter
from ..models import OpenEvent
import io
import base64
from datetime import datetime

pixel_bp = Blueprint('pixel', __name__)

@pixel_bp.route('/<pixel_id>.png', methods=['GET'])
@limiter.limit("10 per minute") # Rate limit specifically for pixel
def track_pixel(pixel_id):
    # Log the open event
    try:
        # Find tracker to ensure it exists
        tracker = mongo.db.trackers.find_one({"pixel_id": pixel_id})
        if tracker:
            user_agent = request.headers.get('User-Agent')
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            
            # Simple GeoIP lookup could go here, for now just store what we have
            
            new_event = OpenEvent(
                tracker_id=tracker['_id'],
                ip_address=ip_address,
                user_agent=user_agent
            )
            mongo.db.open_events.insert_one(new_event.to_dict())
    except Exception as e:
        print(f"Error logging pixel: {e}")

    # Return 1x1 transparent pixel
    # 1x1 transparent GIF
    pixel_data = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    
    response = send_file(
        io.BytesIO(pixel_data),
        mimetype='image/gif',
        max_age=0
    )
    
    # Cache busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response
