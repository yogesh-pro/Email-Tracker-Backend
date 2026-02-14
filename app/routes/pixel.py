
from flask import Blueprint, send_file, request
from ..extensions import mongo, limiter
from ..models import OpenEvent
import io
import base64
import re
from datetime import datetime

pixel_bp = Blueprint('pixel', __name__)

def parse_device(user_agent):
    """Parse User-Agent string to determine device type."""
    if not user_agent:
        return "Unknown"
    
    ua = user_agent.lower()
    
    # Email proxies
    if 'googleimageproxy' in ua or 'gmail' in ua:
        return "Email Proxy"
    if 'outlook' in ua or 'microsoft' in ua:
        return "Desktop"
    if 'yahoo' in ua:
        return "Email Proxy"
    
    # Mobile devices
    if any(m in ua for m in ['iphone', 'android', 'mobile', 'windows phone', 'blackberry']):
        # Check for tablet (iPad, Android tablet)
        if 'ipad' in ua:
            return "Tablet"
        if 'android' in ua and 'mobile' not in ua:
            return "Tablet"
        return "Mobile"
    
    # Tablets
    if 'ipad' in ua or 'tablet' in ua:
        return "Tablet"
    
    # Desktop
    if any(d in ua for d in ['windows', 'macintosh', 'linux', 'x11', 'cros']):
        return "Desktop"
    
    # Bots
    if any(b in ua for b in ['bot', 'crawler', 'spider', 'curl', 'wget']):
        return "Email Proxy"
    
    return "Unknown"

@pixel_bp.route('/<pixel_id>.png', methods=['GET'])
@limiter.limit("10 per minute") # Rate limit specifically for pixel
def track_pixel(pixel_id):
    # Log the open event
    try:
        # Find tracker to ensure it exists
        tracker = mongo.db.trackers.find_one({"pixel_id": pixel_id})
        if tracker:
            user_agent = request.headers.get('User-Agent')
            if request.headers.getlist("X-Forwarded-For"):
                ip_address = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
            else:
                ip_address = request.remote_addr
            
            # Parse device type
            device_type = parse_device(user_agent)
            
            # Debug Info
            print(f"PIXEL ACCESS: {pixel_id} | IP: {ip_address} | UA: {user_agent} | Device: {device_type}")

            should_log = True

            # 1. Ignore if within 10 seconds of creation (Self-open/Preview)
            # Ensure tracker has created_at
            if 'created_at' in tracker:
                age = (datetime.utcnow() - tracker['created_at']).total_seconds()
                if age < 2:
                    print(f"Ignored immediate open (Age: {age}s)")
                    should_log = False

            # 2. Debounce Check: Check last event for this tracker (Ignore IP for strict debounce)
            # If ANY open happened in the last 30s, ignore.
            if should_log:
                # Check last event specifically for this IP
                last_event = mongo.db.open_events.find_one(
                    {"tracker_id": tracker['_id'], "ip_address": ip_address},
                    sort=[("timestamp", -1)]
                )
                
                if last_event:
                    time_diff = (datetime.utcnow() - last_event['timestamp']).total_seconds()
                    if time_diff < 30:
                        should_log = False
                        print(f"Debounced open from IP {ip_address} (last open {time_diff}s ago)")

            if should_log:
                new_event = OpenEvent(
                    tracker_id=tracker['_id'],
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_type=device_type
                )
                mongo.db.open_events.insert_one(new_event.to_dict())
                print(f"LOGGED SUCCESS: {pixel_id} from {ip_address} ({device_type})")
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

