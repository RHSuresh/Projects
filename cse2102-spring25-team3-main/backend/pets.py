import sqlite3
from flask import Blueprint, request, jsonify, current_app, session
from initdatabase import get_db_connection

pets_bp = Blueprint("pets", __name__, url_prefix="/api")

# get info about pets
@pets_bp.route("/pets", methods=["GET"])
def list_pets():
    """
    Get a list of pets
    ---
    tags:
      - Pets
    parameters:
      - name: pet_id
        in: query
        type: string
        required: false
      - name: species
        in: query
        type: string
        required: false
      - name: breed
        in: query
        type: string
        required: false
      - name: age
        in: query
        type: integer
        required: false
      - name: temperament
        in: query
        type: string
        required: false
    responses:
      200:
        description: Pet data retrieval success
      500:
        description: Internal Service Error
    """
    # retrieve query parameters from the GET method
    pet_id = request.args.get("pet_id", type=int)
    species = request.args.get("species", type=str)
    breed = request.args.get("breed", type=str)
    age = request.args.get("age", type=int)
    temperament = request.args.get("temperament", type=str)
    health = request.args.get("health", type=str)


    filters = {
        "pet_id": pet_id,
        "species": species,
        "breed": breed,
        "age": age,
        "temperament": temperament,
        "health": health
    }

    # Use the DB name from app config, default: "real database", testing: "mock database"
    db_name = current_app.config.get("DB_NAME", "pets_adoption.db")

    return fetch_pets_from_db(filters, db_name)

def fetch_pets_from_db(filters, db_name=None):
    query = "SELECT * FROM pets"
    filter_condition = []  # store filters used
    params = []            # store filter parameters

    # check for filters used
    for key, value in filters.items():
        if value is not None:
            filter_condition.append(f"{key} = ?") # add filter
            params.append(value)                  # add filter parameter

    # update query if filters were used
    if filter_condition:
        query += " WHERE " + (" AND ").join(filter_condition)

    conn = get_db_connection(db_name)  # create conn Object, create connection with database
    cursor = conn.cursor()             # create cursor Object, allows interaction with database

    try:
        cursor.execute(query, tuple(params))
        pets = cursor.fetchall()

        # Ensure unique pet names in the response
        unique_pets = {}
        for pet in pets:
            # Use pet name as key to ensure uniqueness
            if pet["name"] not in unique_pets:
                unique_pets[pet["name"]] = pet

        pet_list = [dict(pet) for pet in unique_pets.values()]

        return jsonify(pet_list), 200

    except sqlite3.Error as error:
        print(f"An error occurred: {error}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        conn.close()  # close connection with database


def check_admin_role():
    # check if user is an admin
    role = session.get("role")

    if role == "admin":
        return jsonify({"message": "Permission granted: admin access"}), 200

    print("admin access denied")
    return jsonify({"error": "Permission denied: no admin access"}), 403


@pets_bp.route("/pets", methods=["POST"])
def add_pets():
    # check if user is an admin
    admin_role_check = check_admin_role()
    if admin_role_check[1] != 200:
        return admin_role_check

    data = request.get_json()
    required = ["name", "species", "breed", "age", "temperament", "health", "notes", "pictureUrl"]

    # check for missing fields and store pet data to insert
    try:
        pet_data = [data[field] for field in required]
    except KeyError as missing_field:
        return jsonify({"error": f"Missing required information: {missing_field}"}), 400

    # connect to database
    db_name = current_app.config.get("DB_NAME", "pets_adoption.db")
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    try:
        # check for duplication
        cursor.execute("""
            SELECT * FROM pets
            WHERE name = ? AND species = ? AND breed = ? AND age = ? AND temperament = ? AND pictureURL = ?
        """, (data["name"], data["species"], data["breed"], data["age"], data["temperament"], data["pictureUrl"]))
        if cursor.fetchone():
            return jsonify({"error":"Duplicate pet entry"}), 409

        # insert the new pet info into the database
        cursor.execute("""
            INSERT INTO pets (name, species, breed, age, temperament, health, notes, pictureUrl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(pet_data))
        conn.commit()
        return jsonify({"message": "Pet added successfully", "pet_id": cursor.lastrowid}), 201

    except sqlite3.Error as sqlite_error:
        print(f"An error occurred: {sqlite_error}")
        return jsonify({"error":"Internal Server Error"}), 500

    finally:
        conn.close()


@pets_bp.route("/pets/<int:pet_id>", methods=["PUT"])
def update_pet(pet_id):

    # check if user is an admin
    admin_role_check = check_admin_role()
    if admin_role_check[1] != 200:
        return admin_role_check

    data = request.get_json()
    fields = ["name", "species", "breed", "age", "temperament", "health", "notes", "pictureUrl"]

    updates = []
    values = []

    for field in fields:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])

    if not updates:
        return jsonify({"error": "No fields to update"}), 400
    values.append(pet_id)
    conn = get_db_connection("pets_adoption.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE pets SET {', '.join(updates)} WHERE pet_id = ?", tuple(values))
    conn.commit()
    conn.close()
    return jsonify({"message": "Pet updated successfully"}), 200


@pets_bp.route("/pets/<int:pet_id>", methods=["DELETE"])
def delete_pet(pet_id):

    # check if user is an admin
    admin_role_check = check_admin_role()
    if admin_role_check[1] != 200:
        return admin_role_check

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pets WHERE pet_id = ?", (pet_id,))
    conn.commit()
    rows = cursor.rowcount
    conn.close()

    if rows == 0:
        return jsonify({"error": "Pet not found"}), 404
    return jsonify({"message": "Pet deleted successfully"}), 200
