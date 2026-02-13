
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

load_dotenv()

uri = os.environ.get('MONGO_URI')
print(f"Testing connection to: {uri.split('@')[-1]}") # Don't print password

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("Server available.")
    
    # Check auth
    print("Checking authentication...")
    db = client.get_database() # Uses database from URI
    print(f"Connected to database: {db.name}")
    print("Collections:", db.list_collection_names())
    print("SUCCESS: Connection and Authentication Verified!")
except ConnectionFailure:
    print("Server not available")
except OperationFailure as e:
    print(f"Authentication failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
