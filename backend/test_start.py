
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing Python...")
print(f"Python version: {sys.version}")
print(f"Current dir: {os.getcwd()}")

try:
    import uvicorn
    print("uvicorn imported successfully")
except ImportError as e:
    print(f"Failed to import uvicorn: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("FastAPI app imported successfully")
except ImportError as e:
    print(f"Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStarting server on 0.0.0.0:8000...")
try:
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()

