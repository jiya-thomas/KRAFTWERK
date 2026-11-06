import os
import sys

# Make sure Python can find the app folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    print("  Server started!")
    print("  Open your browser at: http://localhost:8000")
    print("  Press Ctrl+C to stop the server")
    print()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
