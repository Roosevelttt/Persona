"""
Configuration settings for the Persona music recommendation system.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Spotify API settings
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8501/callback")

# Model settings
MODEL_PATH = MODELS_DIR / "music_recommender.joblib"
RANDOM_STATE = 42

# Audio features to use for recommendations (when available)
AUDIO_FEATURES = [
    'danceability',
    'energy',
    'key',
    'loudness',
    'mode',
    'speechiness',
    'acousticness',
    'instrumentalness',
    'liveness',
    'valence',
    'tempo'
]

# Fallback features using basic song metadata
FALLBACK_FEATURES = [
    'popularity',
    'duration_ms',
    'explicit',
    'track_number'
]

# App settings
DEFAULT_SEARCH_LIMIT = 50
MAX_RECOMMENDATIONS = 10
CACHE_DURATION_HOURS = 24

# UI settings
APP_TITLE = "🎵 Persona - AI Music Recommendations"
APP_DESCRIPTION = "Discover music that matches your taste with AI-powered recommendations"
