from flask import Blueprint, jsonify, request
from database import db, redis_client
from models import Message, User
import pika, json
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity

chat_bp = Blueprint("chat", __name__)

# RabbitMQ Connection
def get_rabbitmq_channel():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            Config.RABBITMQ_HOST, Config.RABBITMQ_PORT, '/', 
            pika.PlainCredentials('guest', 'guest'),
            heartbeat=600
        ))
        channel = connection.channel()
        channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
        return connection, channel
    except pika.exceptions.AMQPConnectionError:
        return None, None

# Send Public Message 
@chat_bp.route("/send_public_message", methods=["POST"])
@jwt_required()
def send_public_message():
    data = request.json
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    message = data.get("message")
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    formatted_message = f"{user.username}: {message}"
    redis_client.lpush("general", formatted_message)
    redis_client.ltrim("general", 0, 49)
    redis_client.publish("general", formatted_message)
    
    return jsonify({"message": "Message sent successfully!"}), 200

# Get Public Message
@chat_bp.route("/get_public_messages", methods=["GET"])
def get_public_messages():
    messages = redis_client.lrange("general", 0, 49)  # Get last 50 messages
    
    # Decode only if message is in bytes, else return as is
    decoded_messages = [msg.decode("utf-8") if isinstance(msg, bytes) else msg for msg in messages]
    
    print("Sending Public Messages:", decoded_messages)  # log

    return jsonify({"messages": decoded_messages}), 200

# Send Private Message 
@chat_bp.route("/send_private_message", methods=["POST"])
@jwt_required()
def send_private_message():
    data = request.json
    sender_id = get_jwt_identity()
    receiver_username = data.get("receiver")
    message_text = data.get("message")

    if not receiver_username or not message_text:
        return jsonify({"error": "Receiver and message are required"}), 400

    receiver_user = User.query.filter_by(username=receiver_username).first()
    if not receiver_user:
        return jsonify({"error": "Receiver user not found"}), 404

    connection, channel = get_rabbitmq_channel()
    if not channel:
        return jsonify({"error": "RabbitMQ is not connected"}), 500

    try:
        private_message = json.dumps({
            "sender_id": sender_id,
            "receiver_id": receiver_user.id,
            "message": message_text
        })

        print(f"Sending private message to RabbitMQ: {private_message}")  # Debugging

        channel.basic_publish(
            exchange='',
            routing_key=Config.RABBITMQ_QUEUE,
            body=private_message
        )
        return jsonify({"message": "Private message sent successfully!"}), 200
    finally:
        connection.close()

# Get Private Messages 
@chat_bp.route("/get_private_messages", methods=["GET"])
@jwt_required()
def get_private_messages():
    user_id = get_jwt_identity()
    receiver_username = request.args.get("receiver")
    
    if not receiver_username:
        return jsonify({"error": "Receiver username is required"}), 400
    
    receiver_user = User.query.filter_by(username=receiver_username).first()
    if not receiver_user:
        return jsonify({"error": "Receiver user not found"}), 404
    
    messages = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == receiver_user.id)) |
        ((Message.sender_id == receiver_user.id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp).all()
    
    message_list = [
        {"sender": message.sender.username, "message": message.message, "timestamp": message.timestamp}
        for message in messages
    ]
    
    return jsonify({"messages": message_list}), 200