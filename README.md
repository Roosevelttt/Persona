# Persona - AI Music Recommendation System

A real-time, personalized music recommendation application that learns from user feedback using machine learning.

## 🎯 Features

- 🎵 **Real-time Recommendations** - Get instant music suggestions using Spotify API
- 🤖 **Machine Learning** - SGDClassifier with incremental learning adapts to your taste
- 👍👎 **Simple Feedback** - Like/dislike system for continuous improvement
- 🔄 **Dynamic Updates** - Recommendations improve with each interaction
- 📊 **Audio Analysis** - Uses Spotify's audio features for intelligent matching
- 💾 **Smart Caching** - Efficient data storage and model persistence
- 📱 **Responsive UI** - Clean, intuitive Streamlit interface

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
python setup.py
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your Spotify credentials

# 3. Run the application
streamlit run app.py
```

## 📋 Prerequisites

- **Python 3.8+**
- **Spotify Developer Account** (free)
- **Internet connection** for API access

## 🔧 Spotify API Setup

1. **Create Spotify App:**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Click "Create an App"
   - Fill in app name and description
   - Accept terms and create

2. **Get Credentials:**
   - Copy **Client ID** and **Client Secret**
   - Add them to your `.env` file:
   ```env
   SPOTIFY_CLIENT_ID=your_actual_client_id
   SPOTIFY_CLIENT_SECRET=your_actual_client_secret
   ```

3. **No Redirect URI needed** - We use Client Credentials flow

## 🏗️ Project Architecture

```
persona/
├── app.py                 # 🎨 Main Streamlit UI application
├── music_recommender.py   # 🧠 ML recommendation engine
├── spotify_client.py      # 🎵 Spotify API integration
├── data_manager.py        # 💾 Data processing & storage
├── config.py             # ⚙️  Configuration settings
├── setup.py              # 🛠️ Automated setup script
├── models/               # 🤖 Trained model storage
├── data/                 # 📊 Cache and user feedback
└── requirements.txt      # 📦 Python dependencies
```

## 🎮 How to Use

1. **Start the App:**
   ```bash
   streamlit run app.py
   ```

2. **First Song:**
   - App loads and shows an initial song recommendation
   - Listen to the 30-second preview
   - Click the Spotify link for the full song

3. **Provide Feedback:**
   - Click 👍 **Like** if you enjoy the song
   - Click 👎 **Dislike** if it's not your taste
   - The AI learns from each interaction

4. **Watch It Learn:**
   - Each feedback improves future recommendations
   - Statistics show your rating history
   - Recommendations become more personalized over time

## 🧠 How It Works

### Machine Learning Pipeline
1. **Audio Features:** Extracts 11 audio characteristics from Spotify
   - Danceability, Energy, Valence, Tempo, etc.
2. **SGD Classifier:** Uses incremental learning for real-time updates
3. **Feature Scaling:** Normalizes audio features for consistent predictions
4. **Preference Modeling:** Learns patterns from your like/dislike feedback

### Recommendation Process
1. **Initial Model:** Starts with balanced synthetic training data
2. **User Feedback:** Updates model with `partial_fit()` after each rating
3. **Prediction:** Ranks all unrated songs by preference probability
4. **Selection:** Shows highest-scoring song as next recommendation

## 🛠️ Technical Details

### Dependencies
- **Streamlit** - Web application framework
- **Scikit-learn** - Machine learning (SGDClassifier)
- **Spotipy** - Spotify API client
- **Pandas/NumPy** - Data processing
- **Joblib** - Model persistence

### Data Storage
- **Models:** Saved in `models/` directory with joblib
- **Cache:** Song data cached in `data/songs_cache.json`
- **Feedback:** User ratings stored in `data/user_feedback.csv`

### API Usage
- **Client Credentials Flow** - No user login required
- **Audio Features API** - Extracts musical characteristics
- **Search API** - Finds diverse songs across genres
- **Rate Limiting** - Respects Spotify API limits

## 🔧 Troubleshooting

### Common Issues

**"Spotify credentials not found"**
- Ensure `.env` file exists with correct credentials
- Check that variable names match exactly: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`

**"Failed to fetch songs from Spotify"**
- Verify your Spotify API credentials are valid
- Check internet connection
- Ensure your Spotify app is not rate-limited

**"Model not trained yet"**
- This is normal on first run - the app creates initial training data
- Start rating songs to improve the model

**App runs slowly**
- First run takes longer due to data fetching and caching
- Subsequent runs use cached data for faster startup

### Performance Tips
- Rate at least 10-15 songs for noticeable improvements
- The model learns continuously - more feedback = better recommendations
- Clear cache by deleting `data/songs_cache.json` to refresh song database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with semantic messages: `git commit -m "feat: add new feature"`
5. Push and create a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Spotify** for providing the comprehensive music API
- **Streamlit** for the excellent web app framework
- **Scikit-learn** for robust machine learning tools

---

**🎵 Enjoy discovering your perfect music with Persona!**
