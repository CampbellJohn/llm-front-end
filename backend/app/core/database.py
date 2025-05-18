from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from app.core.config import settings
import logging
import asyncio

class MongoDB:
    client: AsyncIOMotorClient = None
    db: Database = None

async def connect_to_mongo():
    """
    Connect to MongoDB database
    """
    try:
        print(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        
        # Connect with retry logic
        for attempt in range(10):  # Increased number of attempts
            try:
                # Parse connection options from URL
                MongoDB.client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    serverSelectionTimeoutMS=10000,  # Increased timeout
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000,
                    retryWrites=True,
                    maxPoolSize=50,
                    minPoolSize=10,
                    waitQueueTimeoutMS=10000
                )
                
                # Force a connection to verify it works
                # Use the database from the connection string
                db_name = settings.MONGODB_DB_NAME
                MongoDB.db = MongoDB.client[db_name]
                
                # Test the connection with a simple command
                await MongoDB.db.command('ping')
                
                print(f"Successfully connected to MongoDB database '{db_name}'")
                
                # Create indexes if needed
                await create_indexes()
                return
            except Exception as e:
                print(f"Connection attempt {attempt+1} failed: {str(e)}")
                if attempt < 9:  # Don't sleep on the last attempt
                    await asyncio.sleep(5)  # Increased wait time between retries
                else:
                    raise
    except Exception as e:
        print(f"Failed to connect to MongoDB after multiple attempts: {str(e)}")
        logging.error(f"MongoDB connection error: {str(e)}")
        raise

async def create_indexes():
    """Create indexes for collections"""
    try:
        # Create index for conversations collection
        await MongoDB.db.conversations.create_index("id", unique=True)
        print("Created indexes for MongoDB collections")
    except Exception as e:
        print(f"Error creating indexes: {str(e)}")
        logging.error(f"Error creating indexes: {str(e)}")

async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    if MongoDB.client:
        MongoDB.client.close()
        print("Closed MongoDB connection")

def get_database() -> Database:
    """
    Get MongoDB database instance
    """
    if MongoDB.db is None:
        print("Warning: Attempting to get database before connection is established")
        raise RuntimeError("Database connection not established")
    return MongoDB.db
