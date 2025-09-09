import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import joblib

# Load all datasets
print("Loading data...")
songs_df = pd.read_csv('Data Set/songs_with_audio_feature.csv')
albums_df = pd.read_csv('Data Set/albums.csv')
artists_df = pd.read_csv('Data Set/artists.csv')

print(f"Songs: {len(songs_df)}")
print(f"Albums: {len(albums_df)}")
print(f"Artists: {len(artists_df)}")

# Merge datasets to enrich the data
print("Merging datasets...")

# First, expand artist_ids and artist_names from lists to individual rows for better analysis
songs_expanded = []
for idx, row in songs_df.iterrows():
    artist_ids = eval(row['artist_ids']) if isinstance(row['artist_ids'], str) else row['artist_ids']
    artist_names = eval(row['artist_names']) if isinstance(row['artist_names'], str) else row['artist_names']

    for artist_id, artist_name in zip(artist_ids, artist_names):
        song_copy = row.copy()
        song_copy['primary_artist_id'] = artist_id
        song_copy['primary_artist_name'] = artist_name
        songs_expanded.append(song_copy)

songs_expanded_df = pd.DataFrame(songs_expanded)

# Merge with albums
songs_with_albums = songs_expanded_df.merge(albums_df, on='album_id', how='left')

# Merge with artists
songs_complete = songs_with_albums.merge(artists_df, left_on='primary_artist_id', right_on='artist_id', how='left')

print(f"Complete dataset: {len(songs_complete)} songs")

# Remove duplicates based on track_id, keeping the first occurrence
songs_complete = songs_complete.drop_duplicates(subset='track_id', keep='first')

print(f"After removing duplicates: {len(songs_complete)} songs")

# Select features for recommendation (including artist features)
features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness',
           'liveness', 'loudness', 'speechiness', 'tempo', 'key', 'mode', 'explicit',
           'popularity_x', 'followers', 'popularity_y']  # popularity_x is song popularity, popularity_y is artist popularity

# Handle missing values
songs_complete = songs_complete.dropna(subset=features)

print(f"After cleaning: {len(songs_complete)} songs")

# Scale features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(songs_complete[features])

# Train NearestNeighbors model for recommendations
nn = NearestNeighbors(n_neighbors=10, metric='cosine')
nn.fit(scaled_features)

# Save the model and scaler
joblib.dump(nn, 'music_recommender.pkl')
joblib.dump(scaler, 'scaler.pkl')
songs_complete.to_pickle('songs_df.pkl')

print("Enhanced model trained and saved successfully!")
print(f"Features used: {features}")