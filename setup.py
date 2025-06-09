"""
Setup script for the Persona music recommendation system.
"""

import os
import sys
from pathlib import Path
import subprocess

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories."""
    print("📁 Setting up directories...")
    directories = ["models", "data"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

def check_env_file():
    """Check if .env file exists and guide user to set it up."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        if env_example.exists():
            print("📋 Please copy .env.example to .env and add your Spotify credentials:")
            print("   1. Go to https://developer.spotify.com/dashboard/")
            print("   2. Create a new app")
            print("   3. Copy Client ID and Client Secret to .env file")
            print(f"   4. Run: cp {env_example} {env_file}")
        return False
    else:
        print("✅ .env file found")
        
        # Check if credentials are set
        with open(env_file, 'r') as f:
            content = f.read()
            if "your_spotify_client_id_here" in content or "your_spotify_client_secret_here" in content:
                print("⚠️  Please update your Spotify credentials in .env file")
                return False
        
        print("✅ Spotify credentials appear to be configured")
        return True

def run_setup():
    """Run the complete setup process."""
    print("🎵 Setting up Persona - AI Music Recommendation System")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Setup directories
    setup_directories()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check environment file
    env_ready = check_env_file()
    
    print("\n" + "=" * 50)
    if env_ready:
        print("🎉 Setup completed successfully!")
        print("\n🚀 To start the application, run:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Setup completed with warnings")
        print("\n📝 Next steps:")
        print("   1. Set up your Spotify API credentials in .env file")
        print("   2. Run: streamlit run app.py")
    
    print("\n📚 For more information, see README.md")
    return True

if __name__ == "__main__":
    run_setup()
