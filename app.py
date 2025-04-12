from flask import Flask, request, jsonify, redirect, send_from_directory
from flask_cors import CORS
import os
import requests
import base64
import json
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify Client class
class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.api_base_url = "https://api.spotify.com/v1/"

    def get_auth_url(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "user-top-read playlist-modify-public playlist-modify-private"
        }
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url

    def get_access_token(self, code):
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        response = requests.post(self.token_url, headers=headers, data=data)
        return response.json()

    def get_top_artists(self, access_token, time_range="medium_term", limit=10):
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"{self.api_base_url}me/top/artists"
        params = {"time_range": time_range, "limit": limit}
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()

    def get_top_tracks(self, access_token, time_range="medium_term", limit=10):
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"{self.api_base_url}me/top/tracks"
        params = {"time_range": time_range, "limit": limit}
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()

    def create_playlist(self, access_token, user_id, name, description):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        endpoint = f"{self.api_base_url}users/{user_id}/playlists"
        data = json.dumps({
            "name": name,
            "description": description,
            "public": False
        })
        response = requests.post(endpoint, headers=headers, data=data)
        return response.json()

    def add_tracks_to_playlist(self, access_token, playlist_id, track_uris):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        endpoint = f"{self.api_base_url}playlists/{playlist_id}/tracks"
        data = json.dumps({"uris": track_uris})
        response = requests.post(endpoint, headers=headers, data=data)
        return response.json()

    def get_recommendations(self, access_token, seed_artists=None, seed_tracks=None, limit=20):
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"{self.api_base_url}recommendations"
        params = {"limit": limit}

        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:5])
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:5])

        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()

    def get_user_profile(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"{self.api_base_url}me"
        response = requests.get(endpoint, headers=headers)
        return response.json()

# Set up Flask app
app = Flask(__name__, static_folder='frontend')
app.secret_key = os.urandom(24)

# Configure CORS to allow requests from the Render URL itself and localhost
RENDER_URL = "https://spotify-playlist-creator-1a7x.onrender.com"
CORS(app, resources={r"/*": {"origins": [RENDER_URL, "http://localhost:5000", "http://127.0.0.1:5000"]}}, supports_credentials=True)

# Get Spotify credentials from environment variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# Make sure the redirect URI includes the /callback path
base_redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:5000")
REDIRECT_URI = base_redirect_uri + ("/callback" if not base_redirect_uri.endswith("/callback") else "")

# Debug: Print redirect URI (remove in production)
print(f"ORIGINAL REDIRECT_URI: {base_redirect_uri}")
print(f"FINAL REDIRECT_URI: {REDIRECT_URI}")

# Create Spotify client
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

    # Redirect back to the Render URL with the access token
    return redirect(f"{RENDER_URL}/#access_token={access_token}")

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

# New endpoint to just get recommendations without creating a playlist
@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    try:
        print("Received request to /get-recommendations")
        data = request.json
        if not data:
            print("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400

        prompt = data.get('prompt', '')
        print(f"Received prompt: {prompt}")

        # Create a static list of recommendations based on common genres
        # This avoids the need to call the Spotify API

        # Define some sample tracks for different genres/moods
        rock_tracks = [
            {"name": "Bohemian Rhapsody", "artists": [{"name": "Queen"}]},
            {"name": "Sweet Child O' Mine", "artists": [{"name": "Guns N' Roses"}]},
            {"name": "Stairway to Heaven", "artists": [{"name": "Led Zeppelin"}]},
            {"name": "Back in Black", "artists": [{"name": "AC/DC"}]},
            {"name": "Smells Like Teen Spirit", "artists": [{"name": "Nirvana"}]}
        ]

        pop_tracks = [
            {"name": "Shape of You", "artists": [{"name": "Ed Sheeran"}]},
            {"name": "Blinding Lights", "artists": [{"name": "The Weeknd"}]},
            {"name": "Bad Guy", "artists": [{"name": "Billie Eilish"}]},
            {"name": "Uptown Funk", "artists": [{"name": "Mark Ronson"}, {"name": "Bruno Mars"}]},
            {"name": "Shake It Off", "artists": [{"name": "Taylor Swift"}]}
        ]

        electronic_tracks = [
            {"name": "Strobe", "artists": [{"name": "deadmau5"}]},
            {"name": "Levels", "artists": [{"name": "Avicii"}]},
            {"name": "Scary Monsters and Nice Sprites", "artists": [{"name": "Skrillex"}]},
            {"name": "Titanium", "artists": [{"name": "David Guetta"}, {"name": "Sia"}]},
            {"name": "Clarity", "artists": [{"name": "Zedd"}, {"name": "Foxes"}]}
        ]

        chill_tracks = [
            {"name": "Weightless", "artists": [{"name": "Marconi Union"}]},
            {"name": "Gymnopédie No.1", "artists": [{"name": "Erik Satie"}]},
            {"name": "Clair de Lune", "artists": [{"name": "Claude Debussy"}]},
            {"name": "Intro", "artists": [{"name": "The xx"}]},
            {"name": "Porcelain", "artists": [{"name": "Moby"}]}
        ]

        study_tracks = [
            {"name": "Experience", "artists": [{"name": "Ludovico Einaudi"}]},
            {"name": "River Flows In You", "artists": [{"name": "Yiruma"}]},
            {"name": "Nuvole Bianche", "artists": [{"name": "Ludovico Einaudi"}]},
            {"name": "Comptine d'un autre été", "artists": [{"name": "Yann Tiersen"}]},
            {"name": "Time", "artists": [{"name": "Hans Zimmer"}]}
        ]

        workout_tracks = [
            {"name": "Eye of the Tiger", "artists": [{"name": "Survivor"}]},
            {"name": "Till I Collapse", "artists": [{"name": "Eminem"}]},
            {"name": "Stronger", "artists": [{"name": "Kanye West"}]},
            {"name": "Can't Hold Us", "artists": [{"name": "Macklemore & Ryan Lewis"}]},
            {"name": "Power", "artists": [{"name": "Kanye West"}]}
        ]

        # Select tracks based on the prompt
        prompt_lower = prompt.lower()
        selected_tracks = []

        if any(word in prompt_lower for word in ['rock', 'guitar', 'band', 'classic rock']):
            selected_tracks.extend(rock_tracks)

        if any(word in prompt_lower for word in ['pop', 'catchy', 'radio', 'mainstream']):
            selected_tracks.extend(pop_tracks)

        if any(word in prompt_lower for word in ['electronic', 'edm', 'dance', 'club', 'dj']):
            selected_tracks.extend(electronic_tracks)

        if any(word in prompt_lower for word in ['chill', 'relax', 'calm', 'peaceful', 'ambient']):
            selected_tracks.extend(chill_tracks)

        if any(word in prompt_lower for word in ['study', 'focus', 'concentration', 'work', 'piano']):
            selected_tracks.extend(study_tracks)

        if any(word in prompt_lower for word in ['workout', 'exercise', 'gym', 'run', 'energetic']):
            selected_tracks.extend(workout_tracks)

        # If no specific genre/mood was detected, provide a mix
        if not selected_tracks:
            selected_tracks.extend(rock_tracks[:1])
            selected_tracks.extend(pop_tracks[:1])
            selected_tracks.extend(electronic_tracks[:1])
            selected_tracks.extend(chill_tracks[:1])
            selected_tracks.extend(study_tracks[:1])

        # Limit to 10 tracks
        import random
        if len(selected_tracks) > 10:
            selected_tracks = random.sample(selected_tracks, 10)

        return jsonify({
            "name": f"Recommendations based on: {prompt[:30]}",
            "tracks": selected_tracks
        })
    except Exception as e:
        print(f"Unexpected error in get_recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    try:
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
    except Exception as e:
        print(f"Error in create_playlist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/user-profile')
def user_profile():
    access_token = request.args.get('access_token')
    profile = spotify_client.get_user_profile(access_token)
    return jsonify(profile)

# Debug route to check configuration
@app.route('/debug')
def debug():
    return jsonify({
        "status": "ok",
        "redirect_uri": REDIRECT_URI,
        "render_url": RENDER_URL
    })

# Serve frontend files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

if __name__ == '__main__':
    app.run(debug=True)
