"""
Debug environment variables loading.
"""

import os
from dotenv import load_dotenv

print("🔍 Debugging environment variables...")

# Load .env file
load_dotenv()

print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

# Check environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

print(f"SPOTIFY_CLIENT_ID: {client_id}")
print(f"SPOTIFY_CLIENT_SECRET: {client_secret}")

if client_id and client_secret:
    print("✅ Credentials found!")
else:
    print("❌ Credentials not found!")
    
    # Try reading .env file directly
    try:
        with open('.env', 'r') as f:
            content = f.read()
            print("\n📄 .env file content:")
            print(content)
    except Exception as e:
        print(f"Error reading .env file: {e}")
