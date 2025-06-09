"""
Data management utilities for the Persona music recommendation system.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta

from config import DATA_DIR, AUDIO_FEATURES, CACHE_DURATION_HOURS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Manages data storage, caching, and preprocessing for the music recommendation system."""
    
    def __init__(self):
        self.cache_file = DATA_DIR / "songs_cache.json"
        self.feedback_file = DATA_DIR / "user_feedback.csv"
        self.songs_data = {}
        self.feedback_data = pd.DataFrame()
        
    def load_cached_songs(self) -> Dict:
        """Load cached song data from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(cache_data.get('timestamp', '1970-01-01'))
                if datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS):
                    logger.info(f"Loaded {len(cache_data.get('songs', {}))} songs from cache")
                    return cache_data.get('songs', {})
                else:
                    logger.info("Cache expired, will refresh data")
                    
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
            
        return {}
    
    def save_songs_cache(self, songs_data: Dict) -> None:
        """Save song data to cache file."""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'songs': songs_data
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Cached {len(songs_data)} songs")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def load_feedback_data(self) -> pd.DataFrame:
        """Load user feedback data from CSV file."""
        try:
            if self.feedback_file.exists():
                df = pd.read_csv(self.feedback_file)
                logger.info(f"Loaded {len(df)} feedback records")
                return df
        except Exception as e:
            logger.warning(f"Error loading feedback data: {e}")
            
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=['song_id', 'feedback', 'timestamp'] + AUDIO_FEATURES)
    
    def save_feedback(self, song_id: str, feedback: int, audio_features: Dict) -> None:
        """Save user feedback to CSV file."""
        try:
            # Create new feedback record
            new_record = {
                'song_id': song_id,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add audio features
            for feature in AUDIO_FEATURES:
                new_record[feature] = audio_features.get(feature, 0)
            
            # Load existing data and append
            df = self.load_feedback_data()
            new_df = pd.DataFrame([new_record])
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Save to file
            df.to_csv(self.feedback_file, index=False)
            logger.info(f"Saved feedback for song {song_id}")
            
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
    
    def prepare_features_for_ml(self, audio_features: Dict) -> np.ndarray:
        """Convert audio features dictionary to numpy array for ML model."""
        features = []
        for feature in AUDIO_FEATURES:
            features.append(audio_features.get(feature, 0))
        return np.array(features).reshape(1, -1)
    
    def get_song_features_batch(self, songs_data: Dict) -> Tuple[List[str], np.ndarray]:
        """Extract features for multiple songs for batch prediction."""
        song_ids = []
        features_list = []
        
        for song_id, song_data in songs_data.items():
            if 'audio_features' in song_data:
                song_ids.append(song_id)
                features = []
                for feature in AUDIO_FEATURES:
                    features.append(song_data['audio_features'].get(feature, 0))
                features_list.append(features)
        
        return song_ids, np.array(features_list) if features_list else np.array([]).reshape(0, len(AUDIO_FEATURES))
