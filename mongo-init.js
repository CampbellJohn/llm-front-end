// mongo-init.js
// This script will be executed when the MongoDB container is created

// This script runs as the root user when MongoDB is first initialized

// Create admin user if it doesn't exist
db.createUser({
  user: 'admin',
  pwd: 'password',
  roles: [{ role: 'root', db: 'admin' }]
});

print('Admin user created successfully');

// Switch to the application database
db = db.getSiblingDB('llm_chat_db');

// Create application database user
db.createUser({
  user: 'app_user',
  pwd: 'password',
  roles: [{ role: 'readWrite', db: 'llm_chat_db' }]
});

// Create collections
db.createCollection('conversations');

// Create indexes
db.conversations.createIndex({ "id": 1 }, { unique: true });

print('MongoDB initialization completed successfully');
