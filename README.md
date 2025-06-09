# Persona - AI Music Recommendation System

A real-time, personalized music recommendation application that learns from user feedback using machine learning.

## Features

- 🎵 Real-time music recommendations using Spotify API
- 🤖 Machine learning with SGDClassifier for incremental learning
- 👍👎 Simple feedback system for continuous improvement
- 🔄 Dynamic recommendation updates based on user preferences
- 📊 Audio feature analysis for better recommendations

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Spotify API credentials (see `.env.example`)
4. Run the application: `streamlit run app.py`

## Requirements

- Python 3.8+
- Spotify Developer Account
- Internet connection for API access

## Project Structure

```
persona/
├── app.py                 # Main Streamlit application
├── music_recommender.py   # ML recommendation engine
├── spotify_client.py      # Spotify API integration
├── data_manager.py        # Data processing utilities
├── config.py             # Configuration settings
├── models/               # Trained model storage
├── data/                 # Sample data and cache
└── requirements.txt      # Python dependencies
```
