
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import mongo

app = create_app()

with app.app_context():
    try:
        users_count = mongo.db.users.count_documents({})
        print(f"Total users in DB: {users_count}")
        if users_count > 0:
            user = mongo.db.users.find_one()
            # Handle potential mismatch if old users still exist with email but no username
            print(f"Sample user: {user.get('username', 'No username (legacy user with email: ' + user.get('email', 'unknown') + ')')}")
        else:
            print("No users found. Please register first.")
    except Exception as e:
        print(f"Error accessing DB: {e}")
