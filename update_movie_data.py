import tmdbsimple as tmdb
import pandas as pd
import json

# Set your TMDb API key
tmdb.API_KEY = 'a4cf07ebd6aff6e44c9646d06ae65fcf'  # Replace with your actual TMDb API key

# Load the existing dataset
movies = pd.read_csv("movies_enhanced.csv")

# Function to fetch movie data from TMDb
def fetch_movie_data(title):
    try:
        search = tmdb.Search()
        response = search.movie(query=title)
        
        if not search.results:
            return None
        
        # Get the first result
        movie_id = search.results[0]['id']
        movie = tmdb.Movies(movie_id)
        info = movie.info()
        credits = movie.credits()
        
        # Extract relevant fields
        metadata = {
            "Title": info['title'],
            "Description": info['overview'],
            "Genre": ", ".join([genre['name'] for genre in info['genres']]),
            "Year": info['release_date'].split("-")[0],
            "Director": next((crew['name'] for crew in credits['crew'] if crew['job'] == 'Director'), "Unknown"),
            "Runtime": info['runtime'],
            "Language": info['original_language'],
            "Poster": f"https://image.tmdb.org/t/p/w500{info['poster_path']}"
        }
        return metadata
    except Exception as e:
        print(f"Error fetching data for {title}: {e}")
        return None

# Update the dataset with real descriptions and metadata
for index, row in movies.iterrows():
    title = row['title']
    print(f"Fetching data for: {title}")
    
    # Fetch data from TMDb
    metadata = fetch_movie_data(title)
    
    if metadata:
        # Update the movie's description and metadata
        movies.at[index, "description"] = metadata["Description"]
        movies.at[index, "metadata"] = json.dumps(metadata)
    else:
        print(f"No data found for: {title}")

# Save the updated dataset
movies.to_csv("movies_enhanced.csv", index=False)
print("Dataset updated successfully.")