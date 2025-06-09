"""
Quick test to verify Spotify API credentials work.
"""

from dotenv import load_dotenv
from spotify_client import SpotifyClient

def test_spotify_connection():
    """Test Spotify API connection and basic functionality."""
    print("🎵 Testing Spotify API Connection...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize Spotify client
        client = SpotifyClient()
        print("✅ Spotify client initialized successfully")
        
        # Test search functionality
        print("🔍 Testing song search...")
        songs = client.search_songs("The Beatles", limit=10)
        
        if songs:
            print(f"✅ Found {len(songs)} songs")
            
            # Show first song
            first_song_id = list(songs.keys())[0]
            first_song = songs[first_song_id]
            print(f"📀 Sample song: {first_song['name']} by {first_song['artist']}")
            
            # Test audio features
            print("🎼 Testing audio features...")
            features = client.get_audio_features([first_song_id])
            
            if features:
                print("✅ Audio features retrieved successfully")
                sample_features = features[first_song_id]
                print(f"   Danceability: {sample_features.get('danceability', 'N/A')}")
                print(f"   Energy: {sample_features.get('energy', 'N/A')}")
                print(f"   Valence: {sample_features.get('valence', 'N/A')}")
            else:
                print("❌ Failed to get audio features")
                return False
                
        else:
            print("❌ No songs found")
            return False
            
        print("\n🎉 All tests passed! Spotify API is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_spotify_connection()
    if not success:
        print("\n💡 Make sure your .env file has valid Spotify credentials:")
        print("   SPOTIFY_CLIENT_ID=your_actual_client_id")
        print("   SPOTIFY_CLIENT_SECRET=your_actual_client_secret")
