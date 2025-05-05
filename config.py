import os

class Config:
    # SQLAlchemy Configuration for PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', "postgresql://postgres:root@postgres/postgres")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', "redis")
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # RabbitMQ Configuration
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', "rabbitmq")
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', "private_messages")

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', "3f7a9c4b2d8e1f6c9a0b5e3d7c4f8e1a2b6d0c9a5f7e3d1b8c0a4f9d2e6b7c3")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    