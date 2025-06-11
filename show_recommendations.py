"""
Show current recommendations and model predictions.
"""

from dotenv import load_dotenv
from spotify_client import SpotifyClient
from music_recommender import MusicRecommender
from data_manager import DataManager
import pandas as pd

def show_current_recommendations():
    """Display current recommendations and model state."""
    print("🎵 Persona - Current Recommendations Analysis")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    data_manager = DataManager()
    recommender = MusicRecommender()
    spotify_client = SpotifyClient()
    
    # Load feedback data
    feedback_df = data_manager.load_feedback_data()
    print(f"📊 Your Rating History:")
    print(f"   Total songs rated: {len(feedback_df)}")
    if not feedback_df.empty:
        likes = len(feedback_df[feedback_df['feedback'] == 1])
        dislikes = len(feedback_df[feedback_df['feedback'] == 0])
        print(f"   👍 Likes: {likes}")
        print(f"   👎 Dislikes: {dislikes}")
        print(f"   📈 Like ratio: {likes/(likes+dislikes)*100:.1f}%")
    
    # Load songs data
    songs_data = data_manager.load_cached_songs()
    if not songs_data:
        print("\n❌ No cached songs found. Please run the main app first.")
        return
    
    print(f"\n🎼 Song Database:")
    print(f"   Total songs available: {len(songs_data)}")
    
    # Get rated songs
    rated_song_ids = set(feedback_df['song_id'].tolist()) if not feedback_df.empty else set()
    unrated_songs = {sid: data for sid, data in songs_data.items() if sid not in rated_song_ids}
    print(f"   Unrated songs: {len(unrated_songs)}")
    
    # Get recommendations
    if recommender.is_trained and unrated_songs:
        print(f"\n🤖 AI Model Status:")
        stats = recommender.get_model_stats()
        print(f"   Model trained: {'✅' if stats['is_trained'] else '❌'}")
        print(f"   Training data: {stats['total_feedback']} samples")
        
        print(f"\n🎯 Top 10 Recommendations:")
        recommendations = recommender.predict_preferences(songs_data, exclude_ids=list(rated_song_ids))
        
        for i, (song_id, score) in enumerate(recommendations[:10], 1):
            song = songs_data[song_id]
            print(f"   {i:2d}. {song['name'][:40]:<40} by {song['artist'][:25]:<25} (Score: {score:.3f})")
        
        # Show current top recommendation
        if recommendations:
            top_song_id, top_score = recommendations[0]
            top_song = songs_data[top_song_id]
            print(f"\n🌟 Current Top Recommendation:")
            print(f"   Song: {top_song['name']}")
            print(f"   Artist: {top_song['artist']}")
            print(f"   Album: {top_song['album']}")
            print(f"   Confidence Score: {top_score:.3f}")
            if top_song.get('external_url'):
                print(f"   Spotify: {top_song['external_url']}")
    
    else:
        print(f"\n⚠️  Model not ready or no unrated songs available")
    
    print(f"\n💡 Tips:")
    print(f"   • Rate more songs to improve recommendations")
    print(f"   • The model learns from each like/dislike")
    print(f"   • Recommendations get better with more data")
    print(f"   • Check the main app at http://127.0.0.1:8000")

if __name__ == "__main__":
    show_current_recommendations()
