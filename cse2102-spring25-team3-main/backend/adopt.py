import sqlite3
from flask import Blueprint, request, jsonify, session
from initdatabase import get_db_connection

adopt_bp = Blueprint("adopt", __name__, url_prefix="/api")

@adopt_bp.route("/adopts", methods=["POST"])
def adopt_form():
    """
    Adopt application submission
    """
    try:
        data = request.get_json()

        if not data or not data.get("pet_id") or not data.get("user_id"):
            return jsonify({"error": "Missing Required Information"}), 400

        conn = get_db_connection("pets_adoption.db")
        cur = conn.cursor()
        user_id = data.get("user_id")
        pet_id = data.get("pet_id")
        default_status = "Pending"

        # check for duplication
        cur.execute("""
            SELECT * FROM adoption_applications
            WHERE user_id = ? AND pet_id = ?
        """, (data["user_id"], data["pet_id"]))
        if cur.fetchone():
            return jsonify({"error":"Duplicate pet entry"}), 409

        cur.execute("""
        INSERT INTO adoption_applications
        (user_id, pet_id, approval_status)
        VALUES (?, ?, ?)
        """, (user_id, pet_id, default_status))
        conn.commit()
        application_id = cur.lastrowid
        conn.close()
        return jsonify({"status": "submitted", "application_id": application_id}), 201

    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error": "Internal Server Error"}), 500

# Get all adoption form user has applied to
@adopt_bp.route("/adopts/<int:user_id>", methods=["GET"])
def adopt_list(user_id):
    try:
        conn = get_db_connection("pets_adoption.db")
        cur = conn.cursor()
        if session.get("role") == "admin":
            cur.execute("SELECT * FROM adoption_applications")
        else:
            cur.execute("SELECT * FROM adoption_applications WHERE user_id=?", (user_id,))
        adopt_applications = cur.fetchall()
        conn.close()

        adopt_forms = [dict(adopt_app) for adopt_app in adopt_applications]
        return jsonify(adopt_forms), 200
    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error": "Internal Server Error"}), 500

@adopt_bp.route("/adopts/<int:application_id>", methods=["PUT"])
def update_application(application_id):

    data = request.get_json()

    approval_status = data["approval_status"]

    if not approval_status:
        return jsonify({"error": "No fields to update"}), 400

    conn = get_db_connection("pets_adoption.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE adoption_applications SET approval_status=? WHERE application_id = ?", (approval_status, application_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Application updated successfully"}), 200

@adopt_bp.route("/appointments", methods=["POST"])
def appointment_form():
    """
    Appointment application submission
    """
    data = request.get_json()
    if not data or not data.get("user_id") or not data.get("pet_id"):
        return jsonify({"error": "Missing Required Information"}), 400

    try:
        conn = get_db_connection("pets_adoption.db")
        cur = conn.cursor()
        user_id = data.get("user_id")
        pet_id = data.get("pet_id")
        date = data.get("date")
        purpose = data.get("purpose")

        cur.execute("""
        INSERT INTO appointments
        (date, user_id, pet_id, purpose)
        VALUES (?, ?, ?, ?)
        """, (date, user_id, pet_id, purpose))
        conn.commit()
        appointment_id = cur.lastrowid
        conn.close()
        return jsonify({"status": "submitted", "appointment_id": appointment_id}), 201

    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error": "Internal Server Error"}), 500

# Get all appointments, including the user_id and pet_id
@adopt_bp.route("/appointments/<int:user_id>", methods=["GET"])
def appointments_list(user_id):

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM appointments WHERE user_id=?", (user_id,))
        appointments = cur.fetchall()
        conn.close()

        appointment_list = [dict(app) for app in appointments]
        print(appointment_list)
        return jsonify(appointment_list), 200
    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error": "Internal Server Error"}), 500

# Delete an appointment by appointment_id functionality
@adopt_bp.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
        conn.commit()
        rows_deleted = cur.rowcount
        conn.close()

        if rows_deleted == 0:
            return jsonify({"error": "Appointment not found"}), 404

        return jsonify({"message": "Appointment deleted successfully"}), 200
    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error": "Internal Server Error"}), 500
