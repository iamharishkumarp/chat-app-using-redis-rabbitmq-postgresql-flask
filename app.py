from flask import Flask
from flask_cors import CORS
from config import Config
from database import db
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app) 

# Import routes after initializing app & JWT
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp 

# Initialize database
db.init_app(app)

# Enable CORS for your Flask app
CORS(app) # allow all origins

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(chat_bp, url_prefix="/chat")  

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(host="0.0.0.0", port=5000, debug=True)



