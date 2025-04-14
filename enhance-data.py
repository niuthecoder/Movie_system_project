import pandas as pd
import json

# Load the movies dataset
movies = pd.read_csv("movies.csv")

# Function to generate a synthetic description
def generate_description(title, genres):
    return f"A movie about {title.split(' (')[0]}. Genres: {genres.replace('|', ', ')}."

# Function to generate synthetic metadata
def generate_metadata(genres):
    return {
        "Genre": genres.replace("|", ", "),
        "Year": "Unknown",  # Placeholder
        "Rating": "Unknown",  # Placeholder
        "Cast": "Unknown",  # Placeholder
        "imdbRating": "Unknown",  # Placeholder
        "Poster": "https://via.placeholder.com/300x450"  # Placeholder poster
    }

# Add description and metadata columns
movies["description"] = movies.apply(lambda row: generate_description(row["title"], row["genres"]), axis=1)
movies["metadata"] = movies.apply(lambda row: json.dumps(generate_metadata(row["genres"])), axis=1)

# Save the enhanced dataset to a new CSV file
movies.to_csv("movies_enhanced.csv", index=False)

print("Enhanced dataset saved to 'movies_enhanced.csv'.")