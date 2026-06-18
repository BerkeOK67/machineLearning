import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # PostgreSQL
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'ml_platform')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
    
    # Use SQLite for development if PostgreSQL is not available
    USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() == 'true'
    
    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///ml_platform.db'
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'ml_platform')
    MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
    
    # Model storage
    MODEL_FOLDER = 'models'
    
    # AWS
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET = os.getenv('S3_BUCKET', 'ml-platform-datasets')
    USE_AWS = os.getenv('USE_AWS', 'false').lower() == 'true'
    AWS_SAGEMAKER_ROLE = os.getenv('AWS_SAGEMAKER_ROLE')
    SAGEMAKER_INSTANCE_TYPE = os.getenv('SAGEMAKER_INSTANCE_TYPE', 'ml.m5.large')
    SAGEMAKER_ENDPOINT_INSTANCE_TYPE = os.getenv('SAGEMAKER_ENDPOINT_INSTANCE_TYPE', 'ml.m5.large')
    SAGEMAKER_FRAMEWORK_VERSION = os.getenv('SAGEMAKER_FRAMEWORK_VERSION', '1.2-1')
