"""
Main Streamlit application for the Persona music recommendation system.
"""

import streamlit as st
import streamlit.components.v1 as components
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import APP_TITLE, APP_DESCRIPTION, MAX_RECOMMENDATIONS
from spotify_client import SpotifyClient
from music_recommender import MusicRecommender
from data_manager import DataManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Persona - AI Music Recommendations",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'spotify_client' not in st.session_state:
        st.session_state.spotify_client = None
    
    if 'recommender' not in st.session_state:
        st.session_state.recommender = None
    
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    if 'songs_data' not in st.session_state:
        st.session_state.songs_data = {}
    
    if 'current_song' not in st.session_state:
        st.session_state.current_song = None
    
    if 'current_song_id' not in st.session_state:
        st.session_state.current_song_id = None
    
    if 'rated_songs' not in st.session_state:
        st.session_state.rated_songs = set()
    
    if 'feedback_count' not in st.session_state:
        st.session_state.feedback_count = 0
    
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = False

    if 'use_spotify_embed' not in st.session_state:
        st.session_state.use_spotify_embed = True


def initialize_app():
    """Initialize the application components."""
    try:
        with st.spinner("🎵 Initializing Persona..."):
            # Initialize Spotify client
            if st.session_state.spotify_client is None:
                st.session_state.spotify_client = SpotifyClient()
            
            # Initialize recommender
            if st.session_state.recommender is None:
                st.session_state.recommender = MusicRecommender()
            
            # Load or fetch songs data
            if not st.session_state.songs_data:
                # Try to load from cache first
                cached_songs = st.session_state.data_manager.load_cached_songs()
                
                if cached_songs:
                    st.session_state.songs_data = cached_songs
                    st.success(f"Loaded {len(cached_songs)} songs from cache")
                else:
                    # Fetch new songs from Spotify
                    st.info("Fetching fresh music data from Spotify...")
                    songs_data = st.session_state.spotify_client.get_diverse_songs(limit=100)
                    
                    if songs_data:
                        # Enrich with audio features
                        songs_data = st.session_state.spotify_client.enrich_songs_with_features(songs_data)
                        st.session_state.songs_data = songs_data
                        
                        # Cache the data
                        st.session_state.data_manager.save_songs_cache(songs_data)
                        st.success(f"Loaded {len(songs_data)} songs with audio features")
                    else:
                        st.error("Failed to fetch songs from Spotify. Please check your API credentials.")
                        return False
            
            # Train initial model if needed
            if not st.session_state.recommender.is_trained:
                st.info("Training initial recommendation model...")
                st.session_state.recommender.train_initial_model(st.session_state.songs_data)
            
            # Get initial song recommendation
            if st.session_state.current_song is None:
                get_next_recommendation()
            
            st.session_state.app_initialized = True
            return True
            
    except Exception as e:
        st.error(f"Failed to initialize app: {e}")
        logger.error(f"App initialization error: {e}")
        return False


def get_next_recommendation():
    """Get the next song recommendation."""
    try:
        if not st.session_state.songs_data:
            return
        
        # Get recommendations from model
        recommendations = st.session_state.recommender.predict_preferences(
            st.session_state.songs_data,
            exclude_ids=list(st.session_state.rated_songs)
        )
        
        if recommendations:
            # Get the top recommendation
            song_id, score = recommendations[0]
            st.session_state.current_song_id = song_id
            st.session_state.current_song = st.session_state.songs_data[song_id]
            logger.info(f"Next recommendation: {st.session_state.current_song['name']} (score: {score:.3f})")
        else:
            # Fallback to random song
            random_result = st.session_state.spotify_client.get_random_song(st.session_state.songs_data)
            if random_result:
                song_id, song_data = random_result
                st.session_state.current_song_id = song_id
                st.session_state.current_song = song_data
                logger.info("Using random song as fallback")
    
    except Exception as e:
        logger.error(f"Error getting next recommendation: {e}")


def handle_feedback(feedback: int):
    """Handle user feedback and update the model."""
    try:
        if st.session_state.current_song_id and st.session_state.current_song:
            # Save feedback
            audio_features = st.session_state.current_song.get('audio_features', {})
            st.session_state.data_manager.save_feedback(
                st.session_state.current_song_id,
                feedback,
                audio_features
            )
            
            # Update model
            features_array = st.session_state.data_manager.prepare_features_for_ml(audio_features)
            st.session_state.recommender.update_model(features_array, feedback)
            
            # Track feedback
            st.session_state.rated_songs.add(st.session_state.current_song_id)
            st.session_state.feedback_count += 1
            
            # Show feedback confirmation
            feedback_text = "👍 Liked" if feedback == 1 else "👎 Disliked"
            st.success(f"{feedback_text}: {st.session_state.current_song['name']}")
            
            # Get next recommendation
            get_next_recommendation()
            
            # Rerun to update the display
            st.rerun()
            
    except Exception as e:
        st.error(f"Error processing feedback: {e}")
        logger.error(f"Feedback handling error: {e}")


def create_spotify_embed_html(track_id: str, theme: str = "0") -> str:
    """
    Create HTML for Spotify embed iframe with enhanced styling.

    Args:
        track_id: Spotify track ID
        theme: "0" for light theme, "1" for dark theme
    """
    embed_url = f"https://open.spotify.com/embed/track/{track_id}"

    # Enhanced CSS for responsive iframe with better styling
    iframe_html = f"""
    <div style="
        position: relative;
        width: 100%;
        height: 152px;
        margin: 15px 0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
        padding: 2px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    ">
        <div style="
            width: 100%;
            height: 100%;
            border-radius: 10px;
            overflow: hidden;
            background: white;
        ">
            <iframe
                src="{embed_url}?utm_source=generator&theme={theme}"
                width="100%"
                height="152"
                frameborder="0"
                allowfullscreen=""
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy"
                style="border-radius: 10px; display: block;">
            </iframe>
        </div>
    </div>
    <style>
        div:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.2);
        }}
    </style>
    """
    return iframe_html


def validate_spotify_track_id(track_id: str) -> bool:
    """Validate if the track ID is in correct Spotify format."""
    if not track_id or not isinstance(track_id, str):
        return False

    # Spotify track IDs are 22 characters long and contain alphanumeric characters
    return len(track_id) == 22 and track_id.isalnum()


def display_current_song():
    """Display the current song recommendation with Spotify embed player."""
    if not st.session_state.current_song:
        st.warning("No song to display")
        return

    song = st.session_state.current_song
    song_id = song.get('id')

    # Song information
    st.subheader(f"🎵 {song['name']}")
    st.write(f"**Artist:** {song['artist']}")
    st.write(f"**Album:** {song['album']}")

    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Player preference toggle
        player_col1, player_col2 = st.columns([3, 1])
        with player_col1:
            st.markdown("### 🎧 Listen Now")
        with player_col2:
            use_embed = st.toggle("Spotify Player", value=st.session_state.use_spotify_embed, key="embed_toggle")
            st.session_state.use_spotify_embed = use_embed

        # Display appropriate player based on user preference and availability
        if use_embed and song_id:
            # Validate track ID first
            if validate_spotify_track_id(song_id):
                try:
                    # Determine theme based on Streamlit theme (default to light)
                    embed_html = create_spotify_embed_html(song_id, theme="0")
                    components.html(embed_html, height=170)

                    # Subtle success indicator
                    st.caption("🎵 Spotify embed player loaded successfully")

                except Exception as e:
                    logger.warning(f"Failed to load Spotify embed for {song_id}: {e}")
                    st.error("❌ Unable to load Spotify embed player")

                    # Automatic fallback to audio preview
                    if song.get('preview_url'):
                        st.markdown("**🔊 Audio Preview (Fallback)**")
                        st.audio(song['preview_url'])
                        st.caption("Using audio preview as fallback")
                    else:
                        st.info("No preview available for this song")
            else:
                st.warning("⚠️ Invalid Spotify track ID format")
                # Fallback to audio preview
                if song.get('preview_url'):
                    st.markdown("**🔊 Audio Preview**")
                    st.audio(song['preview_url'])
                else:
                    st.info("No preview available for this song")

        elif song.get('preview_url'):
            # Use standard audio preview
            st.audio(song['preview_url'])
            st.caption("🔊 Standard audio preview")

        else:
            # No preview available at all
            st.info("⚠️ No audio preview available for this song")
            if song_id:
                st.caption("Try enabling Spotify Player above for full track access")

    with col2:
        # Song details and actions
        st.markdown("### 📊 Song Info")

        # Display additional song metadata if available
        if song.get('popularity'):
            st.metric("Popularity", f"{song['popularity']}/100")

        if song.get('duration_ms'):
            duration_min = song['duration_ms'] // 60000
            duration_sec = (song['duration_ms'] % 60000) // 1000
            st.metric("Duration", f"{duration_min}:{duration_sec:02d}")

        # External Spotify link
        if song.get('external_url'):
            st.markdown(f"""
            <div style="margin: 15px 0;">
                <a href="{song['external_url']}" target="_blank"
                   style="
                       display: inline-block;
                       padding: 8px 16px;
                       background-color: #1DB954;
                       color: white;
                       text-decoration: none;
                       border-radius: 20px;
                       font-weight: bold;
                       text-align: center;
                   ">
                   🎧 Open in Spotify
                </a>
            </div>
            """, unsafe_allow_html=True)

    # Feedback buttons (full width below)
    st.markdown("### 💭 Rate This Song")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("👍 Like", key="like_btn", use_container_width=True):
            handle_feedback(1)

    with col2:
        if st.button("👎 Dislike", key="dislike_btn", use_container_width=True):
            handle_feedback(0)

    with col3:
        # Add a skip button for better UX
        if st.button("⏭️ Skip Song", key="skip_btn", use_container_width=True):
            get_next_recommendation()
            st.rerun()


def display_stats():
    """Display recommendation statistics."""
    stats = st.session_state.recommender.get_model_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Songs Rated", st.session_state.feedback_count)
    
    with col2:
        st.metric("👍 Likes", stats['positive_feedback'])
    
    with col3:
        st.metric("👎 Dislikes", stats['negative_feedback'])
    
    with col4:
        st.metric("Available Songs", len(st.session_state.songs_data))


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # App header
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    st.divider()
    
    # Initialize app if needed
    if not st.session_state.app_initialized:
        if not initialize_app():
            st.stop()
    
    # Main content
    if st.session_state.app_initialized:
        # Display current song
        display_current_song()
        
        st.divider()
        
        # Display statistics
        st.subheader("📊 Your Music Journey")
        display_stats()
        
        # Progress indicator
        if st.session_state.feedback_count > 0:
            st.info(f"🎯 The more you rate, the better your recommendations become!")
    
    # Sidebar with additional info
    with st.sidebar:
        st.header("About Persona")
        st.write("Persona learns your music taste through your feedback and provides increasingly personalized recommendations.")

        if st.session_state.app_initialized:
            st.subheader("Model Status")
            stats = st.session_state.recommender.get_model_stats()
            st.write(f"**Model Trained:** {'✅' if stats['is_trained'] else '❌'}")
            st.write(f"**Total Feedback:** {stats['total_feedback']}")

            st.divider()

            # Player preferences
            st.subheader("🎵 Player Settings")
            st.write("**Default Player:**")
            default_embed = st.radio(
                "Choose your preferred music player",
                ["Spotify Embed Player", "Audio Preview"],
                index=0 if st.session_state.use_spotify_embed else 1,
                key="default_player_radio"
            )

            # Update session state based on radio selection
            st.session_state.use_spotify_embed = (default_embed == "Spotify Embed Player")

            st.caption("💡 **Tip:** Spotify embed provides full track access, while audio preview offers 30-second clips.")

            if st.button("🔄 Refresh Current Song", use_container_width=True):
                st.rerun()


if __name__ == "__main__":
    main()
