from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from recommend import parse_tags, compute_score
import requests
import math
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)
CORS(app)

# -----------------
# MySQL Connection
# -----------------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user=("root"),
            password=("admin@123"),
            database=("solo"),
            ssl_disabled =True
        )
        return conn
    except Error as e:
        print("Error connecting to MySQL", e)
        return None

        
 #-------Signup------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"message": "Email already registered"}), 400

        # Insert new user
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Error as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# -----------------
# Login Route
# -----------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, password)
        )
        user = cursor.fetchone()
        if user:
            return jsonify({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "message": "Login successful"
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Error as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/user_hobbies", methods=["POST"])
def save_user_hobbies():
    data = request.get_json()
    user_id = data.get("user_id")
    hobbies = data.get("hobbies")  # array of hobby_ids

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # First, delete previous selections for this user
        cursor.execute("DELETE FROM user_hobbies WHERE user_id=%s", (user_id,))
        # Insert new selections
        for hobby_id in hobbies:
            cursor.execute(
                "INSERT INTO user_hobbies (user_id, hobby_id) VALUES (%s, %s)",
                (user_id, hobby_id)
            )
        conn.commit()
        return jsonify({"message": "Hobbies saved successfully"}), 201
    except Error as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/hobbies", methods=["GET"])
def get_hobbies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM hobbies")
        hobbies = cursor.fetchall()
        return jsonify(hobbies), 200
    except Error as e:
        return jsonify({"message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# -----------------
# Traveller Posts
# -----------------

# Create a new travel post
@app.route('/api/solo-traveller', methods=['POST'])
def create_traveller_post():
    data = request.get_json()
    user_id = data.get('user_id')  # equivalent of req.user._id
    destination = data.get('destination')
    description = data.get('description')
    travelDate = data.get('travelDate')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO traveller_posts (user_id, destination, description, travel_date) VALUES (%s, %s, %s, %s)",
            (user_id, destination, description, travelDate)
        )
        conn.commit()
        post_id = cursor.lastrowid
        cursor.execute(
            "SELECT tp.id, tp.destination, tp.description, tp.travel_date, u.name AS user_name, u.email AS user_email "
            "FROM traveller_posts tp JOIN users u ON tp.user_id = u.id WHERE tp.id=%s",
            (post_id,)
        )
        post = cursor.fetchone()
        return jsonify(post), 201
    except Error as e:
        return jsonify({"message": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Get all travel posts
@app.route('/api/solo-traveller', methods=['GET'])
def get_traveller_posts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT tp.id, tp.destination, tp.description, tp.travel_date, u.name AS user_name, u.email AS user_email "
            "FROM traveller_posts tp JOIN users u ON tp.user_id = u.id "
            "ORDER BY tp.created_at DESC"
        )
        posts = cursor.fetchall()
        return jsonify(posts), 200
    except Error as e:
        return jsonify({"message": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Get travel posts by destination
@app.route('/api/solo-traveller/destination/<destination>', methods=['GET'])
def get_traveller_posts_by_destination(destination):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT tp.id, tp.destination, tp.description, tp.travel_date, u.name AS user_name, u.email AS user_email "
            "FROM traveller_posts tp JOIN users u ON tp.user_id = u.id "
            "WHERE tp.destination LIKE %s "
            "ORDER BY tp.created_at DESC",
            (f"%{destination}%",)
        )
        posts = cursor.fetchall()
        return jsonify(posts), 200
    except Error as e:
        return jsonify({"message": str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Get posts created by a specific user
@app.route('/api/solo-traveller/my-posts/<int:user_id>', methods=['GET'])
def get_my_posts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT tp.id, tp.destination, tp.description, tp.travel_date "
            "FROM traveller_posts tp "
            "WHERE tp.user_id = %s "
            "ORDER BY tp.created_at DESC",
            (user_id,)
        )
        posts = cursor.fetchall()
        return jsonify(posts), 200
    except Error as e:
        return jsonify({"message": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Geocode using OpenStreetMap
def geocode_place(name, city=None):
    try:
        query = f"{name}, {city}" if city else name
        res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json"},
            headers={"User-Agent": "solo-traveller-app"}
        )
        data = res.json()
        if data:
            lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
            print(f"Geocoded {name}: {lat}, {lon}")
            return lat, lon
    except Exception as e:
        print("Geocoding error:", e)
    return None, None

# Dummy scoring function — replace with your actual one
def compute_score(place, user_hobbies, user_budget):
    score = 0
    if 'adventure' in place.get('tags', '') and 'adventure' in user_hobbies:
        score += 5
    if place.get('entrance_fee_inr', 0) <= user_budget:
        score += 5
    # Add more logic if needed
    return score

# Parse tags string to list
def parse_tags(tags_str):
    return [t.strip() for t in tags_str.split(',')] if tags_str else []

@app.route('/api/recommendations', methods=['POST'])
def recommendations():
    data = request.get_json()
    user_lat = data.get('lat')
    user_lng = data.get('lng')
    user_budget = data.get('budget')
    user_hobbies = data.get('hobbies', [])

    if user_lat is None or user_lng is None:
        return jsonify({"error": "User location is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM places")
    places = cursor.fetchall()
    print(f"Total places in DB: {len(places)}")

    recs = []
    for p in places:
        lat, lng = geocode_place(p['name'], p.get('city'))
        if lat is None or lng is None:
            print(f"Skipping {p['name']}, could not geocode")
            continue

        distance_km = haversine(user_lat, user_lng, lat, lng)
        print(f"{p['name']} is {distance_km:.2f} km away")

        if distance_km > 50:  # 50 km filter
            print(f"{p['name']} skipped, too far")
            continue

        score = compute_score(p, user_hobbies, user_budget)
        if score == 0:
            print(f"{p['name']} skipped, score=0")
            continue

        recs.append({
            "place": p['name'],
            "city": p.get('city'),
            "state": p.get('state'),
            "description": p.get('description'),
            "tags": parse_tags(p.get('tags', "")),
            "rating": p.get('google_rating'),
            "entrance_fee": p.get('entrance_fee_inr'),
            "distance_km": distance_km,
            "score": score
        })

    recs.sort(key=lambda x: x['score'], reverse=True)
    print(f"Returning {len(recs)} recommendations")
    return jsonify({"recommendations": recs[:15]})


# Get chat messages for a post
@app.route("/api/post/<int:post_id>/chats", methods=["GET"])
def get_post_chats(post_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT pc.id, pc.message, pc.timestamp, u.name AS sender_name
            FROM post_chats pc
            JOIN users u ON pc.sender_id = u.id
            WHERE pc.post_id = %s
            ORDER BY pc.timestamp ASC
        """, (post_id,))
        chats = cursor.fetchall()
        return jsonify(chats)
    except Exception as e:
        print("Error fetching chats:", e)
        return jsonify({"error": str(e)}), 500

# Send
@app.route("/api/post/<int:post_id>/chats", methods=["POST"])
def send_post_chat(post_id):
    data = request.get_json()
    sender_id = data.get("sender_id")
    message = data.get("message")

    if not sender_id or not message:
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # <-- must be dictionary
        cursor.execute("SELECT user_id FROM traveller_posts WHERE id = %s", (post_id,))
        post_owner = cursor.fetchone()
        if not post_owner:
            return jsonify({"error": "Post not found"}), 404

        receiver_id = post_owner['user_id']

        cursor.execute("""
            INSERT INTO post_chats (post_id, sender_id, receiver_id, message)
            VALUES (%s, %s, %s, %s)
        """, (post_id, sender_id, receiver_id, message))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Error sending chat:", e)
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)