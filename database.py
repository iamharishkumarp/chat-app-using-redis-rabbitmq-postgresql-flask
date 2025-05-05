from flask_sqlalchemy import SQLAlchemy
import redis
from config import Config

# This object will be used to interact with the database and define models.
db = SQLAlchemy()

# Redis Connection
redis_client = redis.StrictRedis(
    host=Config.REDIS_HOST, 
    port=Config.REDIS_PORT, 
    db=Config.REDIS_DB, 
    decode_responses=True
)