"""
Spotify API client for the Persona music recommendation system.
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
from typing import Dict, List, Optional, Tuple
import random
import time

from config import (
    DEFAULT_SEARCH_LIMIT,
    AUDIO_FEATURES,
    FALLBACK_FEATURES
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpotifyClient:
    """Handles all Spotify API interactions for music data and audio features."""
    
    def __init__(self):
        self.sp = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Spotify client with credentials."""
        try:
            # Get credentials from environment (reload in case they weren't loaded at import)
            import os
            from dotenv import load_dotenv
            load_dotenv()

            client_id = os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

            if not client_id or not client_secret:
                raise ValueError("Spotify credentials not found. Please check your .env file.")
            
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Test the connection
            self.sp.search(q="test", type="track", limit=1)
            logger.info("Spotify client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            raise
    
    def search_songs(self, query: str = "popular", limit: int = DEFAULT_SEARCH_LIMIT) -> Dict[str, Dict]:
        """Search for songs and return with basic metadata."""
        try:
            results = self.sp.search(q=query, type="track", limit=limit)
            songs_data = {}
            
            for track in results['tracks']['items']:
                song_id = track['id']
                songs_data[song_id] = {
                    'id': song_id,
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'preview_url': track['preview_url'],  # Can be None
                    'external_url': track['external_urls']['spotify'],
                    'popularity': track['popularity'],
                    'duration_ms': track['duration_ms']
                }
            
            logger.info(f"Found {len(songs_data)} songs")
            return songs_data
            
        except Exception as e:
            logger.error(f"Error searching songs: {e}")
            return {}
    
    def get_audio_features(self, song_ids: List[str]) -> Dict[str, Dict]:
        """Get audio features for multiple songs."""
        try:
            # Spotify API allows max 100 IDs per request
            batch_size = 100
            all_features = {}

            for i in range(0, len(song_ids), batch_size):
                batch_ids = song_ids[i:i + batch_size]
                features_response = self.sp.audio_features(batch_ids)

                for features in features_response:
                    if features:  # Some tracks might not have audio features
                        song_id = features['id']
                        # Extract only the features we need
                        audio_features = {}
                        for feature in AUDIO_FEATURES:
                            audio_features[feature] = features.get(feature, 0)

                        all_features[song_id] = audio_features

                # Rate limiting - be nice to Spotify API
                if len(song_ids) > batch_size:
                    time.sleep(0.1)

            logger.info(f"Retrieved audio features for {len(all_features)} songs")
            return all_features

        except Exception as e:
            logger.warning(f"Audio features not available (403 error - app permissions): {e}")
            logger.info("Falling back to basic song metadata for recommendations")
            return {}
    
    def get_song_with_features(self, song_id: str) -> Optional[Dict]:
        """Get complete song data including audio features."""
        try:
            # Get track info
            track = self.sp.track(song_id)
            
            if not track['preview_url']:
                return None
            
            # Get audio features
            features_response = self.sp.audio_features([song_id])
            audio_features = {}
            
            if features_response and features_response[0]:
                for feature in AUDIO_FEATURES:
                    audio_features[feature] = features_response[0].get(feature, 0)
            
            song_data = {
                'id': song_id,
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'preview_url': track['preview_url'],
                'external_url': track['external_urls']['spotify'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'audio_features': audio_features
            }
            
            return song_data

        except Exception as e:
            logger.error(f"Error getting song with features: {e}")
            return None

    def get_diverse_songs(self, genres: List[str] = None, limit: int = DEFAULT_SEARCH_LIMIT) -> Dict[str, Dict]:
        """Get a diverse set of songs from different genres and time periods."""
        if genres is None:
            genres = ['pop', 'rock', 'hip-hop', 'electronic', 'indie', 'jazz', 'classical', 'country']

        all_songs = {}
        songs_per_genre = max(1, limit // len(genres))

        for genre in genres:
            try:
                # Search with different strategies for diversity
                queries = [
                    f"genre:{genre}",
                    f"genre:{genre} year:2020-2024",
                    f"genre:{genre} year:2010-2019",
                    f"genre:{genre} year:2000-2009"
                ]

                for query in queries:
                    if len(all_songs) >= limit:
                        break

                    songs = self.search_songs(query, limit=songs_per_genre)
                    all_songs.update(songs)

                    if len(all_songs) >= limit:
                        break

            except Exception as e:
                logger.warning(f"Error searching genre {genre}: {e}")
                continue

        # Limit to requested number
        if len(all_songs) > limit:
            song_ids = list(all_songs.keys())
            selected_ids = random.sample(song_ids, limit)
            all_songs = {sid: all_songs[sid] for sid in selected_ids}

        return all_songs

    def create_fallback_features(self, song_data: Dict) -> Dict:
        """Create fallback features from basic song metadata when audio features aren't available."""
        fallback_features = {}

        # Normalize popularity (0-100) to 0-1 range
        fallback_features['popularity'] = song_data.get('popularity', 50) / 100.0

        # Normalize duration (typical range 30s-600s) to 0-1 range
        duration_ms = song_data.get('duration_ms', 180000)  # Default 3 minutes
        fallback_features['duration_normalized'] = min(duration_ms / 600000, 1.0)

        # Convert explicit to numeric
        fallback_features['explicit'] = 1.0 if song_data.get('explicit', False) else 0.0

        # Add some synthetic features based on metadata
        # These are rough approximations but better than nothing
        popularity = song_data.get('popularity', 50)
        fallback_features['energy_estimate'] = min(popularity / 80.0, 1.0)  # Popular songs tend to be energetic
        fallback_features['danceability_estimate'] = 0.5  # Neutral default
        fallback_features['valence_estimate'] = min(popularity / 100.0, 1.0)  # Popular songs tend to be positive

        return fallback_features

    def enrich_songs_with_features(self, songs_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """Add audio features to existing song data, with fallback to basic metadata."""
        try:
            song_ids = list(songs_data.keys())
            audio_features = self.get_audio_features(song_ids)

            # Add audio features to song data
            for song_id, features in audio_features.items():
                if song_id in songs_data:
                    songs_data[song_id]['audio_features'] = features

            # For songs without audio features, create fallback features
            songs_with_features = {}
            for song_id, song_data in songs_data.items():
                if 'audio_features' in song_data:
                    # Has real audio features
                    songs_with_features[song_id] = song_data
                else:
                    # Create fallback features
                    song_data['audio_features'] = self.create_fallback_features(song_data)
                    songs_with_features[song_id] = song_data

            if audio_features:
                logger.info(f"Enriched {len(audio_features)} songs with real audio features")
            else:
                logger.info(f"Using fallback features for {len(songs_with_features)} songs (audio features not available)")

            return songs_with_features

        except Exception as e:
            logger.error(f"Error enriching songs with features: {e}")
            return songs_data

    def get_random_song(self, songs_data: Dict[str, Dict]) -> Optional[Tuple[str, Dict]]:
        """Get a random song from the provided songs data."""
        if not songs_data:
            return None

        song_id = random.choice(list(songs_data.keys()))
        return song_id, songs_data[song_id]
