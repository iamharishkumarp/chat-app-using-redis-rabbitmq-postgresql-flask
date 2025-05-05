from database import redis_client

def message_handler(message):
    try:
        data = message["data"]
        # Ensure it's a string, not JSON
        if isinstance(data, str):  
            print(f"New Public Message: {data}")
        else:
            print(f"Unexpected message format: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")

pubsub = redis_client.pubsub()
pubsub.subscribe(**{"general": message_handler})

print("📡 Listening for messages in the 'general' chat room...")
pubsub.run_in_thread(sleep_time=0.01)
