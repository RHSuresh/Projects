import sqlite3
import bcrypt
from flask import current_app

def get_db_connection(db_name=None):
    """get database connection"""
    if db_name is None:
        db_name = current_app.config.get("DB_NAME", "pets_adoption.db")
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db_connection(db_name):
    """initialize database"""
    conn = get_db_connection(db_name)
    create_tables(conn)
    insert_initial_data(conn)
    conn.close()

def create_tables(conn):
    """initialize tables for database"""
    cursor = conn.cursor()
    # pets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            species TEXT,
            breed TEXT,
            age INTEGER,
            temperament TEXT,
            health TEXT,
            notes TEXT,
            pictureUrl TEXT
        )
    """)
    # users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    # applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adoption_applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pet_id INTEGER,
            approval_status TEXT
        )
    """)
    # appointments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date INTEGER,
            user_id INTEGER,
            pet_id INTEGER,
            purpose TEXT
        )
    """)
    conn.commit()

def insert_initial_data(conn):
    cursor = conn.cursor()
    pets = [
        ("Bongo", "Dog", "Golden Retriever", 1, "Energetic", "Good", "Loves walks and fetching balls.", "/static/images/Bongo.jpg"),
        ("Mittens", "Cat", "American Short-hair", 1, "Adaptable", "Good", "Likes to cuddle.", "/static/images/Mittens.jpg"),
        ("Biscuit", "Dog", "German Shepherd", 1, "Protective", "Good", "Very protective and loyal", "/static/images/Biscuit.jpg"),
        ("Roxy", "Cat", "American Short-hair", 1, "Sleeper", "Good", "Likes to eat and sleep", "/static/images/sleeping-cat.jpeg"),
        ("Max", "Dog", "Rottweiler", 1, "Protective", "Good", "Very protective and loyal", "/static/images/rottweiler.jpg")
    ]

    # execute multiple sql insert operations
    cursor.executemany("""
        INSERT OR IGNORE INTO pets
        (name, species, breed, age, temperament, health, notes, pictureUrl)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, pets)

    # This part would not be here in a real world setting
    # There is no way someone would put admin credentials in here
    # High security risks
    password = "adminpass123"
    # hash the password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = ("admin", "admin@gmail.com", hashed_password, "admin")

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (username, email, password, role)
        VALUES(?, ?, ?, ?)
    """, user)

    conn.commit()

if __name__ == "__main__":
    initialize_db_connection("pets_adoption.db")
