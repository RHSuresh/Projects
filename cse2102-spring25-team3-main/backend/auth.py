import sqlite3
import bcrypt
from flask import Blueprint, request, jsonify, current_app, session
from initdatabase import get_db_connection

# Blueprint for authentication endpoints
auth_bp = Blueprint("auth", __name__, url_prefix="/api")

@auth_bp.route("/users", methods=["POST"])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Authentication
    parameters:
      - name: username
        in: body
        type: string
        example: testuser
        required: true
      - name: password
        in: body
        type: string
        example: securePass123
        required: true
      - name: email
        in: body
        type: string
        example: user@example.com
        required: true
    responses:
      201:
        description: User created successfully
      400:
        description: Username and password required
      409:
        description: Username or email already exists
      500:
        description: Internal Server Error
    """
    # get input from frontend
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    default_role = "user"

    # check all fields filled
    if not username or not password:
        return jsonify({"error": "Username, password, and email required"}), 400

    # hash the password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # coonnect to database
    db_name = current_app.config.get("DB_NAME", "pets_adoption.db")
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    try:
        # add new user to database
        cursor.execute(
            "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
            (username, hashed_password, email, default_role)
        )
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201

    except sqlite3.IntegrityError:
        # check for duplicates
        return jsonify({"error": "Username or email already exists"}), 409

    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        conn.close()

@auth_bp.route("/login", methods=["POST"])
def login_user():
    """
    User login
    ---
    tags:
      - Authentication
    parameters:
      - name: username_or_email
        in: body
        type: string
        exmaple: testuser
        required: true
      - name: password
        in: body
        type: string
        example: securePass123
        required: true
    responses:
      200:
        description: Login successful
      400:
        description: Username and password required
      401:
        description: Wrong username or password
      500:
        description: Internal Server Error
    """
    # get input from frontend
    data = request.get_json()
    username_or_email = data.get("username_or_email")
    password = data.get("password")

    # check all fields filled
    if not username_or_email or not password:
        return jsonify({"error": "Username and password required"}), 400

    # connect to database
    db_name = current_app.config.get("DB_NAME", "pets_adoption.db")
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    try:
        # check if username or email exist
        cursor.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()

        # check if password is correct
        if user is None or not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            return jsonify({"error": "Wrong username or password"}), 401

        # intialize session data after login success
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        # set session expiration to PERMANENT_SESSION_TIME (clears session and cookie after expiration)
        session.permanent = True

        # return data
        response = jsonify({
            "message": "Login successful",
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"]
        })

        # set the cookie
        response.set_cookie("session", str(user["user_id"]), httponly=True, secure=True, samesite="Strict")
        return response, 200

    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        conn.close()

@auth_bp.route("/login-status", methods=["GET"])
def login_status():
    """
    Login Status
    ---
    tags:
      - Authentication
    responses:
      200:
        description: login status and info
    """
    if session and "user_id" in session:
        return jsonify({
            "logged_in": True,
            "user_id": session["user_id"],
            "username": session["username"],
            "role": session["role"]
        }), 200

    return jsonify({"message": "User is not logged in", "logged_in": False}), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    User Logout
    ---
    tags:
      - Authentication
    responses:
      200:
        description: logout user session and cookie
    """
    # clear session
    session.clear()

    # return message
    response = jsonify({"message":"logout successful"})

    # clear cookie
    response.set_cookie("secure", "", expires=0,  httponly=True, secure=True, samesite="Strict")

    return response, 200
