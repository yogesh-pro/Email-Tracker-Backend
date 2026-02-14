
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mongo
from bson import ObjectId

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/<tracker_id>', methods=['GET'])
@analytics_bp.route('/<tracker_id>', methods=['GET'])
# @jwt_required()
def get_analytics(tracker_id):
    try:
        # current_user_id = get_jwt_identity()
        client_id = request.args.get('client_id')
        
        try:
            tracker_oid = ObjectId(tracker_id)
        except:
            return jsonify({"message": "Invalid tracker ID"}), 400
        
        query = {"_id": tracker_oid}
        if client_id:
            query["client_id"] = client_id
        
        # Verify ownership or public access
        tracker = mongo.db.trackers.find_one(query)
        
        if not tracker:
            return jsonify({"message": "Tracker not found or unauthorized"}), 404

        # Aggregation for stats
        pipeline = [
            {"$match": {"tracker_id": tracker_oid}},
            {"$sort": {"timestamp": -1}},
            {"$limit": 100} # Limit recent events
        ]
        
        events = list(mongo.db.open_events.aggregate(pipeline))
        
        # Format events
        formatted_events = []
        for event in events:
            formatted_events.append({
                "timestamp": event['timestamp'].isoformat() if event.get('timestamp') else None,
                "ip_address": event.get('ip_address'),
                "user_agent": event.get('user_agent'),
                "device_type": event.get('device_type')
            })
            
        total_opens = mongo.db.open_events.count_documents({"tracker_id": tracker_oid})
        
        return jsonify({
            "tracker_title": tracker['title'],
            "total_opens": total_opens,
            "recent_events": formatted_events
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Server Error: {str(e)}"}), 500
