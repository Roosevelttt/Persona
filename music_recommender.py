"""
Machine learning recommendation engine for the Persona music recommendation system.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from config import MODEL_PATH, RANDOM_STATE, AUDIO_FEATURES
from data_manager import DataManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MusicRecommender:
    """Machine learning recommendation engine using SGDClassifier for incremental learning."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.data_manager = DataManager()
        self.is_trained = False
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the SGDClassifier and StandardScaler."""
        try:
            # Try to load existing model
            if MODEL_PATH.exists():
                self._load_model()
            else:
                # Create new model
                self.model = SGDClassifier(
                    loss='log_loss',  # For probability estimates
                    random_state=RANDOM_STATE,
                    learning_rate='adaptive',
                    eta0=0.01,
                    max_iter=1000,
                    tol=1e-3
                )
                self.scaler = StandardScaler()
                logger.info("Initialized new SGDClassifier model")
                
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise
    
    def _load_model(self) -> None:
        """Load pre-trained model and scaler from disk."""
        try:
            model_data = joblib.load(MODEL_PATH)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = model_data.get('is_trained', False)
            logger.info("Loaded pre-trained model from disk")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fall back to new model
            self._initialize_model()
    
    def _save_model(self) -> None:
        """Save model and scaler to disk."""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, MODEL_PATH)
            logger.info("Model saved to disk")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from user feedback."""
        feedback_df = self.data_manager.load_feedback_data()
        
        if feedback_df.empty:
            return np.array([]).reshape(0, len(AUDIO_FEATURES)), np.array([])
        
        # Extract features and labels
        X = feedback_df[AUDIO_FEATURES].values
        y = feedback_df['feedback'].values
        
        return X, y
    
    def train_initial_model(self, songs_data: Dict[str, Dict], sample_size: int = 20) -> None:
        """Train initial model with synthetic data if no user feedback exists."""
        try:
            X, y = self._prepare_training_data()
            
            if len(X) == 0:
                logger.info("No user feedback found, creating initial training data")
                X, y = self._create_synthetic_training_data(songs_data, sample_size)
            
            if len(X) > 0:
                # Fit scaler on all data
                self.scaler.fit(X)
                X_scaled = self.scaler.transform(X)
                
                # Train model
                self.model.fit(X_scaled, y)
                self.is_trained = True
                self._save_model()
                
                logger.info(f"Initial model trained with {len(X)} samples")
            else:
                logger.warning("No training data available")
                
        except Exception as e:
            logger.error(f"Error training initial model: {e}")
    
    def _create_synthetic_training_data(self, songs_data: Dict[str, Dict], sample_size: int) -> Tuple[np.ndarray, np.ndarray]:
        """Create synthetic training data for initial model."""
        features_list = []
        labels_list = []
        
        # Get songs with audio features
        songs_with_features = [
            (sid, data) for sid, data in songs_data.items() 
            if 'audio_features' in data
        ]
        
        if len(songs_with_features) < sample_size:
            sample_size = len(songs_with_features)
        
        # Create balanced synthetic data
        np.random.seed(RANDOM_STATE)
        selected_songs = np.random.choice(len(songs_with_features), sample_size, replace=False)
        
        for i, idx in enumerate(selected_songs):
            _, song_data = songs_with_features[idx]
            features = [song_data['audio_features'].get(feature, 0) for feature in AUDIO_FEATURES]
            features_list.append(features)
            
            # Create balanced labels (50% like, 50% dislike)
            labels_list.append(1 if i < sample_size // 2 else 0)
        
        return np.array(features_list), np.array(labels_list)
    
    def update_model(self, song_features: np.ndarray, feedback: int) -> None:
        """Update model with new user feedback using incremental learning."""
        try:
            if not self.is_trained:
                logger.warning("Model not trained yet, cannot update")
                return
            
            # Scale features
            song_features_scaled = self.scaler.transform(song_features)
            
            # Update model with partial_fit
            self.model.partial_fit(song_features_scaled, [feedback])
            
            # Save updated model
            self._save_model()
            
            logger.info(f"Model updated with feedback: {feedback}")
            
        except Exception as e:
            logger.error(f"Error updating model: {e}")
    
    def predict_preferences(self, songs_data: Dict[str, Dict], exclude_ids: List[str] = None) -> List[Tuple[str, float]]:
        """Predict user preferences for songs and return ranked recommendations."""
        try:
            if not self.is_trained:
                logger.warning("Model not trained yet, returning random recommendations")
                return self._get_random_recommendations(songs_data, exclude_ids)
            
            if exclude_ids is None:
                exclude_ids = []
            
            # Prepare features for prediction
            song_ids, features_matrix = self.data_manager.get_song_features_batch(songs_data)
            
            if len(features_matrix) == 0:
                return []
            
            # Filter out excluded songs
            filtered_indices = [i for i, sid in enumerate(song_ids) if sid not in exclude_ids]
            if not filtered_indices:
                return []
            
            filtered_song_ids = [song_ids[i] for i in filtered_indices]
            filtered_features = features_matrix[filtered_indices]
            
            # Scale features and predict
            features_scaled = self.scaler.transform(filtered_features)
            
            # Get prediction probabilities
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features_scaled)
                # Get probability of positive class (like)
                scores = probabilities[:, 1] if probabilities.shape[1] > 1 else probabilities[:, 0]
            else:
                # Fallback to decision function
                scores = self.model.decision_function(features_scaled)
            
            # Create ranked recommendations
            recommendations = list(zip(filtered_song_ids, scores))
            recommendations.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error predicting preferences: {e}")
            return self._get_random_recommendations(songs_data, exclude_ids)
    
    def _get_random_recommendations(self, songs_data: Dict[str, Dict], exclude_ids: List[str] = None) -> List[Tuple[str, float]]:
        """Fallback method to get random recommendations."""
        if exclude_ids is None:
            exclude_ids = []
        
        available_songs = [sid for sid in songs_data.keys() if sid not in exclude_ids]
        np.random.shuffle(available_songs)
        
        # Return with random scores
        return [(sid, np.random.random()) for sid in available_songs[:10]]
    
    def get_model_stats(self) -> Dict:
        """Get statistics about the current model."""
        feedback_df = self.data_manager.load_feedback_data()
        
        return {
            'is_trained': self.is_trained,
            'total_feedback': len(feedback_df),
            'positive_feedback': len(feedback_df[feedback_df['feedback'] == 1]) if not feedback_df.empty else 0,
            'negative_feedback': len(feedback_df[feedback_df['feedback'] == 0]) if not feedback_df.empty else 0,
            'model_type': type(self.model).__name__ if self.model else None
        }
