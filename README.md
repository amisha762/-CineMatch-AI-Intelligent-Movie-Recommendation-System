# 🎬 CineMatch AI — Intelligent Movie Recommendation System

An AI-powered, full-stack Movie Recommendation and Discovery Platform built with **Streamlit**, **TF-IDF Natural Language Processing**, **Cosine Similarity**, **SQLite**, and the **The Movie Database (TMDB) API**.

---

## 🌟 Key Features

### 🧠 1. Machine Learning & Recommendation Engine
- **TF-IDF + Cosine Similarity**: Fast content-based filtering across 45,453 movies in the dataset.
- **Hybrid Filters**: Filter recommendations by **Genre**, **Minimum Rating** (0.0 – 10.0), **Release Year Range** (1920 – 2025), and result count (Top 5–20).
- **Match Scoring**: Visual percentage match indicator for every recommended title.
- **Discovery Modes**:
  - **🔥 Trending Movies**: Instant showcase of popular movies.
  - **⭐ Top Rated Classics**: All-time highest-rated masterpieces.
  - **🎲 Surprise Me Pick**: Single-click serendipitous movie generator.
- **TMDB Integration**: Dynamic fallback poster resolution and official YouTube trailer links.

### 🎨 2. Modern Cinematic Glassmorphic Frontend
- Sleek dark cinema theme with modern gradients, translucent cards, glowing badges, and responsive layouts.
- Dynamic genre chips, rating star badges, and match score progress bars.
- Clean sidebar with user profile badge, favorite counts, and intuitive multi-page navigation.

### 🔐 3. Authentication & User Management
- Secure user registration, login, and password recovery.
- Password hashing with **Bcrypt**.
- **⚡ 1-Click Demo Login** for testing and evaluator convenience.
- Profile management: Update full name, change password, and view personal cinema statistics.

### 💾 4. Persistence & Community Interaction
- **❤️ Favorites & Watchlist**: Save movies, filter saved titles, and generate 1-click recommendations from favorites.
- **👍 / 👎 Likes & Dislikes**: Community reaction counters.
- **⭐ Star Ratings (1–5 ⭐)**: Give ratings and compute community average scores.
- **💬 Reviews & Comments**: Community discussion board for every movie.
- **📜 Search History**: Track your recent searches with one-click history clearing.

### 📊 5. Interactive Analytics Dashboard
- **Plotly Visualizations**:
  - Genre distribution across 45,000+ catalog titles.
  - Cinema production trends across decades (1930s – 2020s).
  - Rating vs. Popularity scatter distribution.
  - Top trending search queries across the community.
  - **🧬 Personal CineMatch DNA**: Favorite genre distribution based on user's saved movies.

---

## 📂 Project Architecture

```
Movie Recommendation System/
├── app.py                     # Main Streamlit application entrypoint & router
├── config.py                  # Centralized configuration, dynamic paths & API keys
├── recommendation.py          # TF-IDF recommendation engine, TMDB fetchers & discovery modes
├── database.py                # SQLite database management, schemas & CRUD functions
├── auth.py                    # Bcrypt authentication, registration, session management
├── utils.py                   # CSS loader & UI rendering helpers
├── styles/
│   └── style.css              # Modern dark cinema glassmorphic stylesheet
├── assets/
│   └── default_poster.jpg     # Fallback poster asset
├── pages/
│   ├── login.py               # Sign In page with Demo User access
│   ├── register.py            # Account registration page
│   ├── forgot_password.py     # Password reset page
│   ├── dashboard.py           # Multi-tab discovery, AI recommendations & interactions
│   ├── favorites.py           # Personal Favorites & Watchlist gallery
│   ├── analytics.py           # Plotly analytics & cinema data visualizer
│   └── profile.py             # User profile, history & security settings
├── movie_recommendation.db    # SQLite database (auto-generated & migrated)
├── movies.pkl                 # Precomputed movie tokens dataset
├── tfidf_matrix.pkl           # Precomputed TF-IDF sparse matrix
├── movie_recommendation_cleaned_dataset_v2.csv # Full metadata dataset
├── requirements.txt           # Production Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit theme & server configuration
├── Dockerfile                 # Production Docker container definition
├── docker-compose.yml         # Container orchestration configuration
├── Procfile                   # Cloud PaaS deployment file (Render / Heroku)
├── runtime.txt                # Python runtime specification
└── .env.example               # Environment variables template
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd "Movie Recommendation System"
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. (Optional) Set TMDB API Key
Create a `.env` file or export your key:
```bash
TMDB_API_KEY=your_tmdb_api_key_here
```

### 4. Launch Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🐳 Docker Deployment

### Run with Docker Compose:
```bash
docker-compose up --build
```
Access the application at `http://localhost:8501`.

### Or Build & Run Directly with Docker:
```bash
docker build -t cinematch-ai .
docker run -p 8501:8501 cinematch-ai
```

---

## ☁️ Cloud Deployment (Streamlit Community Cloud / Render / Railway)

### Deploy to Streamlit Community Cloud:
1. Push repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Select your repository, branch `main`, and main file `app.py`.
4. Under **Advanced Settings > Secrets**, optionally add:
   ```toml
   TMDB_API_KEY = "your_tmdb_api_key"
   ```
5. Click **Deploy**!

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit 1.35+, HTML5, CSS3 Glassmorphism
- **Backend / NLP**: Python 3.10+, Scikit-Learn (TF-IDF, Cosine Similarity), Pandas, NumPy
- **Visualizations**: Plotly Express, Plotly Graph Objects
- **Database**: SQLite3 (Thread-Safe with foreign keys & indexes)
- **Security**: Bcrypt password hashing
- **API**: The Movie Database (TMDB) API for posters & video trailers
- **DevOps**: Docker, Docker Compose, Streamlit Cloud, Procfile
