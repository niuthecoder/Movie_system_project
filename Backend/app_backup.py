from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import os
from dotenv import load_dotenv
import requests


# Load environment variables from .env file
load_dotenv()  

# Get the API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the TMDB API key
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Load SentenceTransformer model
try:
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    logger.info("SentenceTransformer model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading SentenceTransformer model: {e}", exc_info=True)
    exit(1)

# Load movie dataset
def load_movie_data():
    """Load movie dataset from a CSV file."""
    try:
        if not os.path.exists("IMDB-Movie-Data.csv"):
            logger.error("File 'IMDB-Movie-Data.csv' not found.")
            return pd.DataFrame()

        movies = pd.read_csv("IMDB-Movie-Data.csv")
        logger.info(f"Dataset columns: {movies.columns}")

        # Check if required columns exist
        required_columns = ["Title", "Description", "Genre", "Director", "Actors", "Year", 
                          "Runtime (Minutes)", "Rating", "Votes", "Revenue (Millions)", "Metascore"]
        for col in required_columns:
            if col not in movies.columns:
                logger.error(f"Required column '{col}' not found in dataset.")
                return pd.DataFrame()

        # Create a "metadata" column
        movies["metadata"] = movies.apply(lambda row: {
            "Genre": row["Genre"],
            "Director": row["Director"],
            "Actors": row["Actors"],
            "Year": row["Year"],
            "Runtime (Minutes)": row["Runtime (Minutes)"],
            "Rating": row["Rating"],
            "Votes": row["Votes"],
            "Revenue (Millions)": row["Revenue (Millions)"],
            "Metascore": row["Metascore"]
        }, axis=1)
        
        logger.info("Movie dataset loaded successfully.")
        return movies
    except Exception as e:
        logger.error(f"Error loading movie dataset: {e}")
        return pd.DataFrame()

# Precompute and cache movie embeddings
def encode_text(text):
    """Encode text into embeddings using SentenceTransformer."""
    try:
        return model.encode([text])[0]
    except Exception as e:
        logger.error(f"Error encoding text: {e}")
        return None

def precompute_movie_embeddings(movies):
    """Precompute embeddings for all movies."""
    try:
        if os.path.exists("movie_embeddings.npy"):
            logger.info("Loading precomputed embeddings from file.")
            movies["embedding"] = list(np.load("movie_embeddings.npy", allow_pickle=True))
        else:
            logger.info("Computing embeddings for all movies. This may take a while...")
            movies["embedding"] = movies["Description"].apply(lambda x: encode_text(x))
            np.save("movie_embeddings.npy", np.array(movies["embedding"]))
        return movies
    except Exception as e:
        logger.error(f"Error precomputing embeddings: {e}")
        return pd.DataFrame()

@app.route('/debug_key')
def debug_key():
    key = os.getenv("TMDB_API_KEY")
    return f"Key exists: {bool(key)} (First 5 chars: {key[:5] if key else 'None'})"

# Fetch poster URL using TMDB API
def fetch_poster(title):
    print(f"Attempting to fetch poster for: {title}")  # Debug line
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("ERROR: TMDB_API_KEY not found in environment variables!")
        return None
        
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    print(f"API URL: {search_url}")  # Debug line
    
    try:
        response = requests.get(search_url)
        print(f"API Response Status: {response.status_code}")  # Debug line
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return None
            
        data = response.json()
        print(f"API Response Data: {data}")  # Debug line
        
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                print(f"Found poster URL: {url}")  # Debug line
                return url
        print("No poster found in API results")
        return None
        
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return None

# Load and preprocess movie data
movies = load_movie_data()
if not movies.empty:
    movies = precompute_movie_embeddings(movies)
else:
    logger.error("No movie data available. Exiting.")
    exit(1)

# Recommendation Endpoint
@app.route("/recommend", methods=["POST"])
def recommend():
    """Recommend movies based on user input."""
    try:
        data = request.json
        user_input = data.get("text", "").strip()

        if not user_input:
            logger.warning("No input provided")
            return jsonify({"error": "No input provided"}), 400

        # Encode user input
        user_embedding = encode_text(user_input)
        if user_embedding is None:
            logger.error("Failed to encode user input.")
            return jsonify({"error": "Failed to encode user input."}), 500

        # Compute similarity between user input and all movies
        movie_embeddings = np.vstack(movies["embedding"])
        similarities = cosine_similarity([user_embedding], movie_embeddings).flatten()

        # Get top 5 recommendations
        top_n = 5
        best_match_indices = np.argsort(similarities)[-top_n:][::-1]
        recommendations = movies.iloc[best_match_indices]

        # Prepare recommendations with posters
        recommendations_with_posters = []
        for idx in range(len(recommendations)):
            movie = recommendations.iloc[idx]
            poster_url = fetch_poster(movie["Title"])
            
            recommendations_with_posters.append({
                "title": movie["Title"],
                "description": movie["Description"],
                "poster": poster_url,
                "metadata": {
                    "Genre": movie["Genre"],
                    "Director": movie["Director"],
                    "Actors": movie["Actors"],
                    "Year": int(movie["Year"]),
                    "Runtime": int(movie["Runtime (Minutes)"]),
                    "Rating": float(movie["Rating"]),
                    "Votes": int(movie["Votes"]),
                    "Revenue": float(movie["Revenue (Millions)"]),
                    "Metascore": float(movie["Metascore"])
                },
                "similarity_score": float(similarities[best_match_indices[idx]])
            })

        logger.info(f"Recommended movies: {[movie['title'] for movie in recommendations_with_posters]}")
        return jsonify({"recommendations": recommendations_with_posters})

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)