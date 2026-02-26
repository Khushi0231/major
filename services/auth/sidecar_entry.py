import uvicorn
import sys
import os

# Add the current directory to sys.path to find 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
