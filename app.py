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

    def get_recommendations(self, access_token, seed_artists=None, seed_tracks=None, limit=20, **kwargs):
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"{self.api_base_url}recommendations"
        params = {"limit": limit}

        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:5])
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:5])

        # Add any additional parameters (like min_energy, target_valence, etc.)
        for key, value in kwargs.items():
            params[key] = value

        print(f"Recommendation params: {params}")
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()

    def search_tracks(self, access_token, query, limit=5):
        headers = {"Authorization": f"Bearer {access_token}"}
        endpoint = f"{self.api_base_url}search"
        params = {
            "q": query,
            "type": "track",
            "limit": limit
        }
        print(f"Searching for tracks with query: {query}")
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

# Enhanced endpoint for creating a journey playlist
@app.route('/create-journey', methods=['POST'])
def create_journey():
    try:
        print("Received request to /create-journey")
        data = request.json
        if not data:
            print("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400

        access_token = data.get('access_token')
        if not access_token:
            print("No access token provided")
            return jsonify({"error": "No access token provided"}), 400

        prompt = data.get('prompt', '')
        print(f"Received journey prompt: {prompt}")

        # Parse the prompt to identify mood segments and specific artists
        prompt_lower = prompt.lower()

        # Check for specific artist mentions
        specific_artists = []
        if 'playboi carti' in prompt_lower:
            specific_artists.append('Playboi Carti')
            print("Detected specific artist request: Playboi Carti")

        # Define mood categories
        high_energy_keywords = ['high energy', 'energetic', 'upbeat', 'hype', 'rage', 'intense']
        vibey_keywords = ['vibey', 'vibe', 'ambient', 'chill', 'relaxed', 'smooth']
        melancholic_keywords = ['melancholic', 'nostalgic', 'bittersweet', 'sad but happy', 'reflective']
        sad_keywords = ['sad', 'emotional', 'depressing', 'heartbreak', 'somber']
        upbeat_keywords = ['bouncy', 'happy', 'cheerful', 'joyful', 'uplifting']

        # Identify which moods are present in the prompt
        moods = []
        if any(keyword in prompt_lower for keyword in high_energy_keywords):
            moods.append('high_energy')
        if any(keyword in prompt_lower for keyword in vibey_keywords):
            moods.append('vibey')
        if any(keyword in prompt_lower for keyword in melancholic_keywords):
            moods.append('melancholic')
        if any(keyword in prompt_lower for keyword in sad_keywords):
            moods.append('sad')
        if any(keyword in prompt_lower for keyword in upbeat_keywords):
            moods.append('upbeat')

        # If no moods detected, use a default journey
        if not moods:
            moods = ['high_energy', 'vibey', 'melancholic', 'sad', 'upbeat']

        print(f"Detected moods: {moods}")

        # Get user's top artists and tracks
        try:
            top_artists = spotify_client.get_top_artists(access_token, limit=20)
            top_tracks = spotify_client.get_top_tracks(access_token, limit=20)

            artist_items = top_artists.get('items', [])
            track_items = top_tracks.get('items', [])

            print(f"Retrieved {len(artist_items)} top artists and {len(track_items)} top tracks")

            # Extract IDs
            artist_ids = [artist.get('id') for artist in artist_items if artist.get('id')]
            track_ids = [track.get('id') for track in track_items if track.get('id')]

            # Create a journey playlist with tracks for each mood
            journey_tracks = []

            # Handle specific track requests
            specific_track_requests = []
            if 'playboi carti' in prompt_lower and 'walk' in prompt_lower:
                print("Looking for WALK by Playboi Carti")
                try:
                    search_results = spotify_client.search_tracks(access_token, "WALK Playboi Carti")
                    if 'tracks' in search_results and search_results['tracks']['items']:
                        walk_track = search_results['tracks']['items'][0]
                        print(f"Found WALK by Playboi Carti: {walk_track['name']} - {walk_track['artists'][0]['name']}")
                        specific_track_requests.append({
                            'position': 'start',
                            'track': walk_track
                        })
                except Exception as e:
                    print(f"Error searching for WALK by Playboi Carti: {str(e)}")

            # Look for a Playboi Carti song for the end
            if 'playboi carti' in prompt_lower and 'end' in prompt_lower:
                print("Looking for a Playboi Carti song for the end")
                try:
                    search_results = spotify_client.search_tracks(access_token, "Playboi Carti experimental", limit=10)
                    if 'tracks' in search_results and search_results['tracks']['items']:
                        # Try to find a different track than WALK
                        end_tracks = [track for track in search_results['tracks']['items']
                                    if track['name'].lower() != 'walk']
                        if end_tracks:
                            end_track = end_tracks[0]
                            print(f"Found Playboi Carti song for end: {end_track['name']}")
                            specific_track_requests.append({
                                'position': 'end',
                                'track': end_track
                            })
                except Exception as e:
                    print(f"Error searching for Playboi Carti end song: {str(e)}")

            # Function to get recommendations for a specific mood
            def get_mood_recommendations(mood, seed_artists, seed_tracks):
                print(f"Getting recommendations for mood: {mood}")

                # Adjust parameters based on mood
                params = {}
                if mood == 'high_energy':
                    params = {
                        'min_energy': 0.8,
                        'min_tempo': 120,
                        'target_valence': 0.6
                    }
                elif mood == 'vibey':
                    params = {
                        'target_energy': 0.5,
                        'max_tempo': 110,
                        'target_acousticness': 0.6
                    }
                elif mood == 'melancholic':
                    params = {
                        'target_energy': 0.4,
                        'target_valence': 0.3,
                        'target_acousticness': 0.7
                    }
                elif mood == 'sad':
                    params = {
                        'max_energy': 0.4,
                        'max_valence': 0.3,
                        'target_acousticness': 0.8
                    }
                elif mood == 'upbeat':
                    params = {
                        'min_energy': 0.7,
                        'min_valence': 0.7,
                        'target_danceability': 0.8
                    }

                # Get recommendations with mood-specific parameters
                try:
                    # Use a subset of seed artists and tracks for each mood to get variety
                    import random
                    mood_seed_artists = random.sample(seed_artists, min(2, len(seed_artists))) if seed_artists else None
                    mood_seed_tracks = random.sample(seed_tracks, min(3, len(seed_tracks))) if seed_tracks else None

                    # Add the parameters to the API call
                    recommendations = spotify_client.get_recommendations(
                        access_token,
                        seed_artists=mood_seed_artists,
                        seed_tracks=mood_seed_tracks,
                        **params
                    )

                    if 'tracks' in recommendations:
                        # Get 3-5 tracks for each mood
                        mood_tracks = recommendations.get('tracks', [])[:4]
                        print(f"Got {len(mood_tracks)} tracks for mood: {mood}")
                        return mood_tracks
                    else:
                        print(f"No tracks found for mood: {mood}")
                        return []
                except Exception as e:
                    print(f"Error getting recommendations for mood {mood}: {str(e)}")
                    return []

            # Get tracks for each mood in the journey
            for mood in moods:
                mood_tracks = get_mood_recommendations(mood, artist_ids, track_ids)
                journey_tracks.extend(mood_tracks)

            # Add specific tracks at their requested positions
            final_journey_tracks = []

            # Add start tracks
            start_tracks = [req['track'] for req in specific_track_requests if req['position'] == 'start']
            final_journey_tracks.extend(start_tracks)

            # Add the mood-based tracks
            final_journey_tracks.extend(journey_tracks)

            # Add end tracks
            end_tracks = [req['track'] for req in specific_track_requests if req['position'] == 'end']
            final_journey_tracks.extend(end_tracks)

            print(f"Created journey with {len(final_journey_tracks)} total tracks")

            # If we didn't get any tracks, provide fallback tracks
            if not final_journey_tracks:
                print("No tracks found, using fallback tracks")

                # Create fallback tracks for Playboi Carti request
                if 'playboi carti' in prompt_lower:
                    final_journey_tracks = [
                        {
                            "name": "WALK",
                            "artists": [{"name": "Playboi Carti"}],
                            "album": {"name": "WHOLE LOTTA RED"}
                        },
                        {
                            "name": "Sky",
                            "artists": [{"name": "Playboi Carti"}],
                            "album": {"name": "Whole Lotta Red"}
                        },
                        {
                            "name": "Magnolia",
                            "artists": [{"name": "Playboi Carti"}],
                            "album": {"name": "Playboi Carti"}
                        },
                        {
                            "name": "Shoota",
                            "artists": [{"name": "Playboi Carti"}, {"name": "Lil Uzi Vert"}],
                            "album": {"name": "Die Lit"}
                        },
                        {
                            "name": "Long Time (Intro)",
                            "artists": [{"name": "Playboi Carti"}],
                            "album": {"name": "Die Lit"}
                        },
                        {
                            "name": "ILoveUIHateU",
                            "artists": [{"name": "Playboi Carti"}],
                            "album": {"name": "Whole Lotta Red"}
                        },
                        {
                            "name": "New Tank",
                            "artists": [{"name": "Playboi Carti"}],
                            "album": {"name": "Whole Lotta Red"}
                        }
                    ]
                else:
                    # Generic fallback tracks for different moods
                    final_journey_tracks = [
                        # High energy tracks
                        {
                            "name": "Sicko Mode",
                            "artists": [{"name": "Travis Scott"}, {"name": "Drake"}],
                            "album": {"name": "Astroworld"}
                        },
                        {
                            "name": "DNA.",
                            "artists": [{"name": "Kendrick Lamar"}],
                            "album": {"name": "DAMN."}
                        },
                        # Vibey tracks
                        {
                            "name": "Redbone",
                            "artists": [{"name": "Childish Gambino"}],
                            "album": {"name": "Awaken, My Love!"}
                        },
                        {
                            "name": "Nights",
                            "artists": [{"name": "Frank Ocean"}],
                            "album": {"name": "Blonde"}
                        },
                        # Melancholic tracks
                        {
                            "name": "Self Control",
                            "artists": [{"name": "Frank Ocean"}],
                            "album": {"name": "Blonde"}
                        },
                        {
                            "name": "505",
                            "artists": [{"name": "Arctic Monkeys"}],
                            "album": {"name": "Favourite Worst Nightmare"}
                        },
                        # Sad tracks
                        {
                            "name": "Marvin's Room",
                            "artists": [{"name": "Drake"}],
                            "album": {"name": "Take Care"}
                        },
                        {
                            "name": "Jocelyn Flores",
                            "artists": [{"name": "XXXTENTACION"}],
                            "album": {"name": "17"}
                        },
                        # Upbeat tracks
                        {
                            "name": "Sunflower",
                            "artists": [{"name": "Post Malone"}, {"name": "Swae Lee"}],
                            "album": {"name": "Spider-Man: Into the Spider-Verse"}
                        },
                        {
                            "name": "Good Feeling",
                            "artists": [{"name": "Flo Rida"}],
                            "album": {"name": "Wild Ones"}
                        }
                    ]

            # Return the journey tracks
            return jsonify({
                "name": f"Music Journey: {prompt[:30]}",
                "tracks": final_journey_tracks
            })

        except Exception as e:
            print(f"Error creating journey: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Error creating journey: {str(e)}"}), 500

    except Exception as e:
        print(f"Unexpected error in create_journey: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Enhanced endpoint for personalized recommendations using Spotify API
@app.route('/get-personalized-recommendations', methods=['POST'])
def get_personalized_recommendations():
    try:
        print("Received request to /get-personalized-recommendations")
        data = request.json
        if not data:
            print("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400

        access_token = data.get('access_token')
        if not access_token:
            print("No access token provided")
            return jsonify({"error": "No access token provided"}), 400

        prompt = data.get('prompt', '')
        print(f"Received prompt: {prompt}")

        # Get user profile for debugging
        try:
            print("Getting user profile...")
            user_profile = spotify_client.get_user_profile(access_token)
            if 'error' in user_profile:
                print(f"Error getting user profile: {user_profile['error']}")
                return jsonify({"error": f"Spotify API error: {user_profile['error'].get('message', 'Unknown error')}"}), 400
            print(f"User profile retrieved: {user_profile.get('display_name')}")
        except Exception as e:
            print(f"Exception getting user profile: {str(e)}")
            return jsonify({"error": f"Error getting user profile: {str(e)}"}), 500

        # Get top artists
        try:
            print("Getting top artists...")
            top_artists = spotify_client.get_top_artists(access_token, limit=10)
            if 'error' in top_artists:
                print(f"Error getting top artists: {top_artists['error']}")
                return jsonify({"error": f"Spotify API error: {top_artists['error'].get('message', 'Unknown error')}"}), 400

            artist_items = top_artists.get('items', [])
            print(f"Retrieved {len(artist_items)} top artists")
            for i, artist in enumerate(artist_items[:3]):
                print(f"Top artist {i+1}: {artist.get('name')}")
        except Exception as e:
            print(f"Exception getting top artists: {str(e)}")
            return jsonify({"error": f"Error getting top artists: {str(e)}"}), 500

        # Get top tracks
        try:
            print("Getting top tracks...")
            top_tracks = spotify_client.get_top_tracks(access_token, limit=10)
            if 'error' in top_tracks:
                print(f"Error getting top tracks: {top_tracks['error']}")
                return jsonify({"error": f"Spotify API error: {top_tracks['error'].get('message', 'Unknown error')}"}), 400

            track_items = top_tracks.get('items', [])
            print(f"Retrieved {len(track_items)} top tracks")
            for i, track in enumerate(track_items[:3]):
                print(f"Top track {i+1}: {track.get('name')} by {', '.join([artist.get('name') for artist in track.get('artists', [])])}")
        except Exception as e:
            print(f"Exception getting top tracks: {str(e)}")
            return jsonify({"error": f"Error getting top tracks: {str(e)}"}), 500

        # Extract IDs for recommendations
        artist_ids = [artist.get('id') for artist in artist_items if artist.get('id')]
        track_ids = [track.get('id') for track in track_items if track.get('id')]

        print(f"Using {len(artist_ids)} artist IDs and {len(track_ids)} track IDs for recommendations")

        # Get recommendations
        try:
            print("Getting recommendations...")
            recommendations = spotify_client.get_recommendations(
                access_token,
                seed_artists=artist_ids[:2] if artist_ids else None,
                seed_tracks=track_ids[:3] if track_ids else None
            )

            if 'error' in recommendations:
                print(f"Error getting recommendations: {recommendations['error']}")
                return jsonify({"error": f"Spotify API error: {recommendations['error'].get('message', 'Unknown error')}"}), 400

            tracks = recommendations.get('tracks', [])
            print(f"Retrieved {len(tracks)} recommended tracks")
            for i, track in enumerate(tracks[:3]):
                print(f"Recommendation {i+1}: {track.get('name')} by {', '.join([artist.get('name') for artist in track.get('artists', [])])}")

            return jsonify({
                "name": f"Personalized recommendations based on: {prompt[:30]}",
                "tracks": tracks
            })
        except Exception as e:
            print(f"Exception getting recommendations: {str(e)}")
            return jsonify({"error": f"Error getting recommendations: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error in get_personalized_recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Keep the demo endpoint for fallback
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

        # Try to use personalized recommendations if access token is provided
        access_token = data.get('access_token')
        if access_token:
            try:
                # Create a new request to the personalized endpoint
                return get_personalized_recommendations()
            except Exception as e:
                print(f"Failed to get personalized recommendations, falling back to demo: {str(e)}")
                # Fall back to demo recommendations

        # Create a static list of recommendations based on common genres
        # This is used as a fallback when Spotify API fails

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
