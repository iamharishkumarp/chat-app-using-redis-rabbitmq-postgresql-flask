from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        """Hashes and sets the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Checks if the password matches the hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Returns user data in dictionary format."""
        return {
            "id": self.id,
            "username": self.username
        }

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships with the User model
    sender = db.relationship("User", foreign_keys=[sender_id])
    receiver = db.relationship("User", foreign_keys=[receiver_id])  

    def to_dict(self):
        """Returns message data in dictionary format."""
        return {
            "id": self.id,
            "sender": self.sender.username if self.sender else None,
            "receiver": self.receiver.username if self.receiver else None,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }