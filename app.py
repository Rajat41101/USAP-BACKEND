from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import json                  
from bson import json_util   
from dotenv import load_dotenv

# Load the secret password from the .env file
load_dotenv()

app = Flask(__name__)

# Allow testing from local files
CORS(app) 

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")

# <-- NEW: Bypasses the strict Mac SSL block for local testing
client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)

# Select your specific database
db = client['Student_hub']

# --- ROUTES ---

# 1. Server test route
@app.route('/', methods=['GET'])
def home():
    return "Backend Server is Running!"

# 2. Database test route
@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        client.admin.command('ping')
        return jsonify({"message": "Successfully connected to MongoDB!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Fetch the notes!
@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        # Go to the 'notes' collection and find everything
        all_notes = list(db.notes.find())
        return json.loads(json_util.dumps(all_notes)), 200
    except Exception as e:
        # <-- NEW: This forces the terminal to print the exact error
        print("\n❌ DATABASE ERROR ❌:")
        print(str(e))
        print("--------------------\n")
        return jsonify({"error": str(e)}), 500
# 4. User Registration Route
@app.route('/api/register', methods=['POST'])
def register():
    try:
        # Get data from frontend
        data = request.json
        email = data.get('email')
        
        # Select the 'users' collection
        users_collection = db['users']

        # Check if user already exists
        if users_collection.find_one({"email": email}):
            return jsonify({"message": "Email already registered"}), 400

        # Create user document
        new_user = {
            "firstName": data.get('firstName'),
            "lastName": data.get('lastName'),
            "email": email,
            "password": data.get('password'), 
            "department": data.get('department'),
            "year": data.get('year'),
            "role": "student"
        }

        # Insert into MongoDB
        result = users_collection.insert_one(new_user)

        return jsonify({
            "message": "User registered successfully!",
            "user": {
                "id": str(result.inserted_id),
                "email": email
            }
        }), 201

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    # Runs the server locally on port 5000
    app.run(debug=True, port=5000)