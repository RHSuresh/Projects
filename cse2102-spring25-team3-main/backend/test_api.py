import unittest
from main import app
from initdatabase import get_db_connection, initialize_db_connection

class TestPetAdoptionAPI(unittest.TestCase):
    """create tests for Pet Adoption API"""

    # === setUp and tearDown === #

    def setUp(self):
        """set up test client"""
        # Configure app
        self.app = app # app instance from main
        self.original_db_name = app.config.get("DB_NAME", "pets_adoption.db") # store original database name
        self.app.config["DB_NAME"] = "pets_adoption_test.db" # store new data base name for testing
        self.app.config["SECRET_KEY"] = "secretkey123" # used to sign test session cookies
        # Table names used in database
        self.tables = ["users", "pets", "adoption_applications", "appointments"]

        # Initialize mock database
        initialize_db_connection(self.app.config["DB_NAME"])      # initialize mock database
        self.conn = get_db_connection(self.app.config["DB_NAME"]) # initialize conn object for mock database connection
        self.cursor = self.conn.cursor()   # initialize cursor object

        # Clear data
        self.clear_table_data() # clear data from tables

        # Create a test client for the Flask app
        self.client = self.app.test_client()
        self.client.testing = True

    def tearDown(self):
        """Clean up after test"""
        # clear pets data
        self.clear_table_data()
        self.app.config["DB_NAME"] = self.original_db_name # switch back to original database name

    # === Helper Functions === #

    def clear_table_data(self):
        """Clear all tables and reset auto-increment"""
        for table in self.tables:
            self.cursor.execute(f"DELETE FROM {table}")
            self.cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")


        self.conn.commit()


    def insert_pet_data(self):
        """insert pet data for testing"""
        # pet data
        pets = [
            ("Bongo", "Dog", "Golden Retriever", 1, "Energetic", "Good", "Loves walks and fetching balls.", "/images/Bongo.jpeg"),
            ("Mittens", "Cat", "American Short-hair", 1, "Adaptable", "Good", "Likes to cuddle.", "/images/Mittens/jpg"),
            ("Biscuit", "Dog", "German Shepherd", 1, "Protective", "Good", "Very protective and loyal", "/images/Biscuit.jpg")
        ]

        # insert pet data
        self.cursor.executemany("""
            INSERT into pets
            (name, species, breed, age, temperament, health, notes, pictureUrl)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """, pets)

        self.conn.commit()

    # === Test Functions === #

    def test_pet_data_no_filter(self):
        """test pet data with no filter"""
        expected_pet_data = [
            {
                "pet_id": 1,
                "name": "Bongo",
                "species": "Dog",
                "breed": "Golden Retriever",
                "age": 1,
                "temperament": "Energetic",
                "health": "Good",
                "notes": "Loves walks and fetching balls.",
                "pictureUrl": "/images/Bongo.jpeg"
            },
            {
                "pet_id": 2,
                "name": "Mittens",
                "species": "Cat",
                "breed": "American Short-hair",
                "age": 1,
                "temperament": "Adaptable",
                "health": "Good",
                "notes": "Likes to cuddle.",
                "pictureUrl": "/images/Mittens/jpg"
            },
            {
                "pet_id": 3,
                "name": "Biscuit",
                "species": "Dog",
                "breed": "German Shepherd",
                "age": 1,
                "temperament": "Protective",
                "health": "Good",
                "notes": "Very protective and loyal",
                "pictureUrl": "/images/Biscuit.jpg"
            }
        ]
        # no filters
        self.insert_pet_data() # insert initial pet data for testing
        response = self.client.get("/api/pets")
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.json, expected_pet_data)


    def test_create_user(self):
        """test create user"""
        response = self.client.post("/api/users", json={"username":"test", "email":"test@example.com", "password":"test"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "User created successfully"})


    def test_create_user_missing_field(self):
        """test create user missing field"""
        response = self.client.post("/api/users", json={"password":"test"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Username, password, and email required"})


    def test_create_user_dup_username(self):
        """test create user duplicate username or email"""
        # first registration
        self.client.post("/api/users",json={"username":"test1", "email":"test1@gmail.com", "password":"test"})

        # dupe registration
        response = self.client.post("/api/users", json={"username":"test1", "email":"test1@gmail.com", "password":"test"})

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json, {"error": "Username or email already exists"})


    def test_login_user(self):
        """test login user"""
        # register initial user
        response = self.client.post("/api/users", json={"username":"test", "email":"test@gmail.com", "password":"test"})
        self.assertEqual(response.status_code, 201)

        # login with username
        response = self.client.post("/api/login", json={"username_or_email":"test", "password":"test"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message":"Login successful", "user_id":1, "username":"test", "role":"user"})

        # login with email
        response = self.client.post("/api/login", json={"username_or_email":"test@gmail.com", "password":"test"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message":"Login successful", "user_id":1, "username":"test", "role":"user"})


    def test_login_missing_field(self):
        """test login user with missing fields"""
        # register initial user
        response = self.client.post("/api/users", json={"username":"test", "email":"test@gmail.com", "password":"test"})
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/api/login", json={"password":"test"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error":"Username and password required"})


    def test_login_invalid_input(self):
        # register initial user
        response = self.client.post("/api/users", json={"username":"test", "email":"test@gmail.com", "password":"test"})
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/api/login", json={"username_or_email":"test1", "password":"test2"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error":"Wrong username or password"})


if __name__ == "__main__":
    unittest.main()
