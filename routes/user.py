from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import create_connection

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    required = ['username', 'full_name', 'email', 'password']
    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    username = data['username']
    full_name = data['full_name']
    email = data['email']
    password = data['password']
    role = data.get('role', 'student')

    if role not in ['student', 'admin']:
        return jsonify({"error": "Role must be student or admin"}), 400

    password_hash = generate_password_hash(password)

    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Users (username, password_hash, full_name, email, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password_hash, full_name, email, role))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400

    username = data['username']
    password = data['password']

    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            return jsonify({
                "message": "Login successful",
                "user_id": user['user_id'],
                "role": user['role']
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
