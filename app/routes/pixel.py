
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
            
            # Debounce Check: Check last event for this tracker & IP
            last_event = mongo.db.open_events.find_one(
                {
                    "tracker_id": tracker['_id'],
                    "ip_address": ip_address
                },
                sort=[("timestamp", -1)]
            )
            
            should_log = True
            if last_event:
                time_diff = (datetime.utcnow() - last_event['timestamp']).total_seconds()
                if time_diff < 30:
                    should_log = False
                    print(f"Debounced open event for {pixel_id} from {ip_address} (last open {time_diff}s ago)")

            if should_log:
                # Geolocation Lookup
                country = None
                city = None
                region = None
                try:
                    # Using ip-api.com (free, no key required for low volume)
                    # Note: HTTP is faster/easier for this free tier
                    geo_url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,city,regionName"
                    import requests
                    geo_resp = requests.get(geo_url, timeout=3)
                    if geo_resp.status_code == 200:
                        geo_data = geo_resp.json()
                        if geo_data.get('status') == 'success':
                            country = geo_data.get('country')
                            city = geo_data.get('city')
                            region = geo_data.get('regionName')
                except Exception as e:
                    print(f"Geo lookup failed: {e}")

                new_event = OpenEvent(
                    tracker_id=tracker['_id'],
                    ip_address=ip_address,
                    user_agent=user_agent,
                    country=country,
                    city=city,
                    region=region
                )
                mongo.db.open_events.insert_one(new_event.to_dict())
                print(f"Logged open event for {pixel_id} from {ip_address} in {city}, {country}")
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
