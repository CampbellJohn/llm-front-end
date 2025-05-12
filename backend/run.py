import uvicorn
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    uvicorn.run(
        "app.main:app",    # Import path to the app
        host="127.0.0.1",  # Bind to localhost
        port=8000,         # Port to listen on
        reload=True        # Auto-reload on code changes
    )
