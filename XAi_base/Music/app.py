from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load model and data
print("Loading model and data...")
nn = joblib.load('music_recommender.pkl')
scaler = joblib.load('scaler.pkl')
songs_df = pd.read_pickle('songs_df.pkl')
print(f"Loaded {len(songs_df)} songs")
print("Sample song:", songs_df.iloc[0]['track_name'])

features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'key', 'mode', 'explicit', 'popularity_x', 'followers', 'popularity_y']

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    track_id = data.get('track_id')
    print(f"Recommend request for track_id: {track_id}")
    if not track_id:
        print("No track_id provided")
        return jsonify({'error': 'track_id required'}), 400

    # Find the song
    song = songs_df[songs_df['track_id'] == track_id]
    if song.empty:
        print(f"Track {track_id} not found")
        return jsonify({'error': 'Track not found'}), 404

    print(f"Found song: {song.iloc[0]['track_name']}")

    # Get features
    song_features = song[features].values
    scaled = scaler.transform(song_features)

    # Find neighbors
    distances, indices = nn.kneighbors(scaled)

    # Get recommended songs
    recs = songs_df.iloc[indices[0][1:]]  # exclude self
    print(f"Recommendations: {len(recs)} songs")
    recommendations = recs[['track_id', 'track_name', 'primary_artist_name', 'album_name', 'album_cover_64x64', 'genres']].to_dict('records')
    # Add audio_url to each recommendation
    for rec in recommendations:
        rec['audio_url'] = f'https://example.com/audio/{rec["track_id"]}.mp3'  # Placeholder

    return jsonify({'recommendations': recommendations})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    print(f"Search query received: '{query}'")
    if not query:
        print("No query provided")
        return jsonify({'error': 'query required'}), 400

    # Simple search by track name
    results = songs_df[songs_df['track_name'].str.contains(query, case=False, na=False)].head(10)
    print(f"Found {len(results)} results for query '{query}'")
    if len(results) > 0:
        print("Sample result:", results.iloc[0]['track_name'])
        # Check for duplicates in results
        unique_tracks = results['track_id'].nunique()
        print(f"Unique tracks in results: {unique_tracks} out of {len(results)} total")
        if unique_tracks != len(results):
            print("WARNING: Duplicates found in search results!")
            # Show duplicate track_ids
            duplicates = results[results.duplicated(subset='track_id', keep=False)]
            if not duplicates.empty:
                print("Duplicate track_ids:", duplicates['track_id'].unique())
    # Add placeholder audio URL for demonstration
    for result in results.itertuples():
        result_dict = result._asdict()
        result_dict['audio_url'] = f'https://example.com/audio/{result.track_id}.mp3'  # Placeholder URL
    search_results = results[['track_id', 'track_name', 'primary_artist_name', 'album_name', 'album_cover_64x64', 'genres']].to_dict('records')
    # Add audio_url to each result
    for i, result in enumerate(search_results):
        result['audio_url'] = f'https://example.com/audio/{result["track_id"]}.mp3'  # Placeholder
    return jsonify({'results': search_results})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)