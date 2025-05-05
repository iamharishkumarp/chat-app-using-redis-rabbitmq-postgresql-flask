import pika, json, time
from database import db
from models import Message, User
from config import Config
from flask import Flask

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def connect_to_rabbitmq(max_retries=5, retry_interval=5):
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{max_retries})...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                Config.RABBITMQ_HOST, Config.RABBITMQ_PORT, '/', 
                pika.PlainCredentials('guest', 'guest')
            ))
            channel = connection.channel()
            print("Connected to RabbitMQ")
            
            # Declare the queue with desired properties
            channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
            print(f"Successfully declared queue: {Config.RABBITMQ_QUEUE}")
            
            return connection, channel
            
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Max retries reached. Exiting...")
                raise

# Try to establish connection
try:
    connection, channel = connect_to_rabbitmq()
except Exception as e:
    print(f"Failed to establish connection after retries: {e}")
    exit(1)

# Callback function to process messages from RabbitMQ
def callback(ch, method, properties, body):
    print(f"Received raw message: {body}")  

    try:
        data = json.loads(body.decode("utf-8"))
        print(f"Decoded message data: {data}")
        
        sender_id = data.get("sender_id")
        receiver_id = data.get("receiver_id")
        message_text = data.get("message")
       
        if not sender_id or not receiver_id or not message_text:
            print(f"Error: Invalid message format - {data}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        with app.app_context():
            sender = User.query.get(sender_id)
            receiver = User.query.get(receiver_id)

            if sender and receiver:
                print(f"Found users - Sender: {sender.username}, Receiver: {receiver.username}")
                new_message = Message(sender_id=sender.id, receiver_id=receiver.id, message=message_text)
                db.session.add(new_message)
                db.session.commit()
                print(f" Private message stored: {sender.username} -> {receiver.username}: {message_text}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(f" Error: Sender or receiver not found")
                if not sender:
                    print(f"Sender with ID {sender_id} not found")
                if not receiver:
                    print(f"Receiver with ID {receiver_id} not found")
                ch.basic_nack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        print(f" Error decoding JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

# Start consuming messages with auto_ack=False
channel.basic_consume(queue=Config.RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=False)
print(f"Listening for messages on queue: {Config.RABBITMQ_QUEUE}")
print("Waiting for private messages...")
channel.start_consuming()



