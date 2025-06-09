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
    SPOTIFY_CLIENT_ID, 
    SPOTIFY_CLIENT_SECRET, 
    DEFAULT_SEARCH_LIMIT,
    AUDIO_FEATURES
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
            if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
                raise ValueError("Spotify credentials not found. Please check your .env file.")
            
            client_credentials_manager = SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
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
                if track['preview_url']:  # Only include songs with preview
                    song_id = track['id']
                    songs_data[song_id] = {
                        'id': song_id,
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'preview_url': track['preview_url'],
                        'external_url': track['external_urls']['spotify'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms']
                    }
            
            logger.info(f"Found {len(songs_data)} songs with previews")
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
            logger.error(f"Error getting audio features: {e}")
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

    def enrich_songs_with_features(self, songs_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """Add audio features to existing song data."""
        try:
            song_ids = list(songs_data.keys())
            audio_features = self.get_audio_features(song_ids)

            # Add audio features to song data
            for song_id, features in audio_features.items():
                if song_id in songs_data:
                    songs_data[song_id]['audio_features'] = features

            # Remove songs without audio features
            songs_with_features = {
                sid: data for sid, data in songs_data.items()
                if 'audio_features' in data
            }

            logger.info(f"Enriched {len(songs_with_features)} songs with audio features")
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
