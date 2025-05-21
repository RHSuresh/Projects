import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from auth import auth_bp
from pets import pets_bp
from adopt import adopt_bp
from flasgger import Swagger
from dotenv import load_dotenv

# create app object
app = Flask(__name__)

# get secret key from environment, used to sign session cookies
load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")

# set global session time
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Swagger configuration and initialization
app.config["SWAGGER"] = {
    "title": "Pet Adoption API",
    "uiversion": 3,
    "openapi": "3.0.2"
}
swagger = Swagger(app)

# Cross Origin Resource Sharing
# - supports_credentials=True - Browser includes cookies in request to backend
# - origin - where the request came from
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(pets_bp)
app.register_blueprint(adopt_bp)

@app.route("/")
def home():
    """home page"""
    return "Welcome to Pet Adoption Website"

if __name__ == "__main__":
    app.run(debug=True)
