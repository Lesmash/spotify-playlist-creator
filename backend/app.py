from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import os
from dotenv import load_dotenv
from spotify_client import SpotifyClient

load_dotenv()

# Debug: Print environment variables (remove in production)
print(f"CLIENT_ID: {os.getenv('SPOTIFY_CLIENT_ID')}")
print(f"REDIRECT_URI: {os.getenv('REDIRECT_URI')}")

# Set up Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure CORS to allow requests from GitHub Pages and localhost
CORS(app, resources={r"/*": {"origins": ["https://<your-github-username>.github.io", "http://localhost:3000", "http://127.0.0.1:3000"]}}, supports_credentials=True)

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")

spotify_client = SpotifyClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

@app.route('/login')
def login():
    auth_url = spotify_client.get_auth_url()
    return jsonify({"auth_url": auth_url})

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = spotify_client.get_access_token(code)

    # In a real app, you'd store tokens securely
    # For this demo, we'll redirect to frontend with token in URL fragment
    access_token = token_info.get('access_token')

    # Redirect to GitHub Pages site
    return redirect(f"https://<your-github-username>.github.io/spotify-playlist-creator/#access_token={access_token}")

@app.route('/top-artists')
def top_artists():
    access_token = request.args.get('access_token')
    time_range = request.args.get('time_range', 'medium_term')
    limit = request.args.get('limit', 10)

    artists = spotify_client.get_top_artists(access_token, time_range, limit)
    return jsonify(artists)

@app.route('/top-tracks')
def top_tracks():
    access_token = request.args.get('access_token')
    time_range = request.args.get('time_range', 'medium_term')
    limit = request.args.get('limit', 10)

    tracks = spotify_client.get_top_tracks(access_token, time_range, limit)
    return jsonify(tracks)

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    data = request.json
    access_token = data.get('access_token')
    prompt = data.get('prompt')

    # Get user profile to get user ID
    user_profile = spotify_client.get_user_profile(access_token)
    user_id = user_profile.get('id')

    # Get top artists and tracks for seeds
    top_artists = spotify_client.get_top_artists(access_token, limit=5)
    top_tracks = spotify_client.get_top_tracks(access_token, limit=5)

    artist_ids = [artist['id'] for artist in top_artists.get('items', [])]
    track_ids = [track['id'] for track in top_tracks.get('items', [])]

    # Get recommendations based on top artists and tracks
    recommendations = spotify_client.get_recommendations(
        access_token,
        seed_artists=artist_ids[:2],
        seed_tracks=track_ids[:3]
    )

    # Create a new playlist
    playlist_name = f"Playlist based on: {prompt[:30]}"
    playlist = spotify_client.create_playlist(
        access_token,
        user_id,
        playlist_name,
        f"Created with prompt: {prompt}"
    )

    # Add tracks to the playlist
    track_uris = [track['uri'] for track in recommendations.get('tracks', [])]
    result = spotify_client.add_tracks_to_playlist(access_token, playlist['id'], track_uris)

    # Get the tracks details to return to frontend
    tracks_details = recommendations.get('tracks', [])

    return jsonify({
        "name": playlist['name'],
        "external_url": playlist['external_urls']['spotify'],
        "tracks": tracks_details
    })

@app.route('/user-profile')
def user_profile():
    access_token = request.args.get('access_token')
    profile = spotify_client.get_user_profile(access_token)
    return jsonify(profile)

# Health check endpoint
@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Spotify Playlist Creator API is running"})

if __name__ == '__main__':
    app.run(debug=True)