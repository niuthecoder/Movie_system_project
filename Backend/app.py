import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import logging

# Initialize
app = Flask(__name__)
CORS(app)
load_dotenv(Path('.')/'.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model Selection ---
#MODEL_NAME = "all-MiniLM-L6-v2"  # 80MB model
MODEL_NAME = "all-mpnet-base-v2"  # 400MB model, better performance
model = SentenceTransformer(MODEL_NAME)
logger.info(f"Loaded model: {MODEL_NAME}")

# --- Data Loading ---
def load_movie_data():
    movies = pd.read_csv("IMDB-Movie-Data.csv")
    
    # Enhanced metadata
    movies["search_text"] = (
        movies["Title"] + " " + 
        movies["Genre"] + " " +
        movies["Actors"] + " " +
        movies["Director"] + " " +
        movies["Description"]
    )
    
    # Precompute embeddings
    if not os.path.exists("embeddings.npy"):
        logger.info("Computing embeddings...")
        embeddings = model.encode(movies["search_text"], show_progress_bar=True)
        np.save("embeddings.npy", embeddings)
    else:
        embeddings = np.load("embeddings.npy")
    
    movies["embedding"] = list(embeddings)
    return movies

movies = load_movie_data()

# --- Enhanced Recommendation ---
def hybrid_score(sim_scores, movie_indices):
    """Combine similarity with movie popularity"""
    scores = []
    for idx, score in zip(movie_indices, sim_scores):
        movie = movies.iloc[idx]
        popularity = (
            0.3 * (movie["Rating"] / 10) + 
            0.2 * (movie["Votes"] / movies["Votes"].max())
        )
        scores.append(score * 0.8 + popularity * 0.2)
    return np.array(scores)

# --- Poster Fetching ---
def fetch_poster(title):
    api_key = os.getenv("TMDB_API_KEY")
    try:
        # Clean title for better matching
        clean_title = title.split("(")[0].strip()
        response = requests.get(
            f"https://api.themoviedb.org/3/search/movie",
            params={"api_key": api_key, "query": clean_title}
        )
        if response.json().get("results"):
            poster_path = response.json()["results"][0].get("poster_path")
            return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    except Exception as e:
        logger.error(f"Poster fetch error: {e}")
    return None

# --- Main Endpoint ---
@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.json
        user_input = data.get("text", "").strip()
        
        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        # Encode input
        input_embedding = model.encode([user_input])[0]
        
        # Calculate similarities
        movie_embeddings = np.vstack(movies["embedding"])
        sim_scores = cosine_similarity([input_embedding], movie_embeddings)[0]
        
        # Get top 5 with hybrid scoring
        top_indices = np.argsort(sim_scores)[-100:][::-1]  # Top 100 candidates
        final_scores = hybrid_score(sim_scores[top_indices], top_indices)
        best_indices = top_indices[np.argsort(final_scores)[-5:][::-1]]
        
        # Prepare results
        results = []
        for idx in best_indices:
            movie = movies.iloc[idx]
            results.append({
                "title": movie["Title"],
                "description": movie["Description"],
                "poster": fetch_poster(movie["Title"]),
                "genre": movie["Genre"],
                "director": movie["Director"],
                "actors": movie["Actors"], 
                "year": int(movie["Year"]),
                "rating": float(movie["Rating"]),
                "runtime": int(movie["Runtime (Minutes)"]),
                "score": float(sim_scores[idx]),
                "votes": int(movie["Votes"]),
                "revenue": float(movie["Revenue (Millions)"]),
                "metascore": float(movie["Metascore"])
            })
        
        return jsonify({"recommendations": results})

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)