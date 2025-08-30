import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from finx.constants import API_CONFIG
    
    print("🚀 Starting FinX Backend Server...")
    print(f"📍 Host: {API_CONFIG['HOST']}")
    print(f"🔌 Port: {API_CONFIG['PORT']}")
    print(f"🔧 Debug: {API_CONFIG['DEBUG']}")
    print(f"🔄 Reload: {API_CONFIG['RELOAD']}")
    
    uvicorn.run(
        "main:app",
        host=API_CONFIG["HOST"],
        port=API_CONFIG["PORT"],
        reload=API_CONFIG["RELOAD"],
        log_level="info"
    )
