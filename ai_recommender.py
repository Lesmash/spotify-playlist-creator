import requests
import json
import os
import random

# Get the Hugging Face API key from environment variables
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

def generate_recommendations(prompt, top_artists=None, top_tracks=None):
    """
    Generate music recommendations using AI based on a prompt and user's top artists/tracks
    """
    try:
        # Check if this is a request for a mixed artist journey with a specific intro track
        prompt_lower = prompt.lower()
        mixed_artist_journey = 'top artists' in prompt_lower and 'journey' in prompt_lower
        specific_intro = 'walk' in prompt_lower and 'playboi carti' in prompt_lower and 'intro' in prompt_lower

        # If we have top artists and it's a mixed journey request, use our specialized function
        if (mixed_artist_journey or specific_intro) and top_artists:
            print("Using specialized mixed artist journey with actual top artists")
            return create_mixed_artist_journey(prompt, top_artists, top_tracks)

        # Check if we have an API key
        if not HUGGINGFACE_API_KEY:
            print("No Hugging Face API key found. Using fallback recommendations.")
            return fallback_recommendations(prompt)
        # Format the user's top artists and tracks
        artists_text = ""
        if top_artists and len(top_artists) > 0:
            artists_text = "Your top artists are: " + ", ".join([artist.get('name', '') for artist in top_artists[:5]])

        tracks_text = ""
        if top_tracks and len(top_tracks) > 0:
            tracks_text = "Your top tracks are: " + ", ".join([
                f"{track.get('name', '')} by {track.get('artists', [{}])[0].get('name', '')}"
                for track in top_tracks[:5]
            ])

        # Create the full prompt for the AI
        full_prompt = f"""
        You are a music recommendation AI that creates personalized playlists.

        {artists_text}
        {tracks_text}

        The user wants a playlist with this description:
        {prompt}

        Create a playlist of 15-20 songs that follows this emotional journey. For each song, provide:
        1. Song title
        2. Artist name
        3. A brief explanation of why this song fits in this part of the journey

        Format your response as a JSON array of objects with the following structure:
        [
            {{
                "title": "Song Title",
                "artist": "Artist Name",
                "album": "Album Name (if known)",
                "mood": "The mood of this song (e.g., energetic, vibey, melancholic, sad, upbeat)",
                "reason": "Brief explanation of why this song fits here"
            }},
            ...
        ]

        Only return the JSON array, nothing else.
        """

        # Call the Hugging Face API
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }

        print("Calling AI model for recommendations...")
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error from Hugging Face API: {response.status_code}")
            print(response.text)
            return fallback_recommendations(prompt)

        # Parse the response
        result = response.json()
        generated_text = result[0].get('generated_text', '')

        # Extract the JSON part from the response
        try:
            # Find the start and end of the JSON array
            json_start = generated_text.find('[')
            json_end = generated_text.rfind(']') + 1

            if json_start == -1 or json_end == 0:
                print("Could not find JSON in response")
                return fallback_recommendations(prompt)

            json_str = generated_text[json_start:json_end]
            recommendations = json.loads(json_str)

            # Validate and clean up the recommendations
            cleaned_recommendations = []
            for rec in recommendations:
                if 'title' in rec and 'artist' in rec:
                    cleaned_rec = {
                        'name': rec['title'],
                        'artists': [{'name': rec['artist']}],
                        'album': {'name': rec.get('album', 'Unknown Album')},
                        'mood': rec.get('mood', ''),
                        'reason': rec.get('reason', '')
                    }
                    cleaned_recommendations.append(cleaned_rec)

            if not cleaned_recommendations:
                return fallback_recommendations(prompt)

            return cleaned_recommendations

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from AI response: {e}")
            print(f"Response text: {generated_text}")
            return fallback_recommendations(prompt)

    except Exception as e:
        print(f"Error generating AI recommendations: {e}")
        return fallback_recommendations(prompt)

def create_mixed_artist_journey(prompt, top_artists, top_tracks):
    """
    Create a journey playlist using the user's actual top artists and specific requirements from the prompt
    """
    print("Creating mixed artist journey with user's actual top artists")
    prompt_lower = prompt.lower()

    # Add randomization based on timestamp to ensure different results each time
    import time
    random.seed(int(time.time()))

    # Check for track limit requests
    track_limit = 20  # Default

    # Look for exact track count specifications
    if 'exactly 12 tracks' in prompt_lower or '12 tracks total' in prompt_lower:
        track_limit = 12
        print(f"User requested exactly {track_limit} tracks")
    elif '10 tracks' in prompt_lower or 'ten tracks' in prompt_lower:
        track_limit = 10
        print(f"User requested {track_limit} tracks")
    elif '15 tracks' in prompt_lower or 'fifteen tracks' in prompt_lower:
        track_limit = 15
        print(f"User requested {track_limit} tracks")
    elif '5 tracks' in prompt_lower or 'five tracks' in prompt_lower:
        track_limit = 5
        print(f"User requested {track_limit} tracks")
    elif '12 tracks' in prompt_lower or 'twelve tracks' in prompt_lower:
        track_limit = 12
        print(f"User requested {track_limit} tracks")

    # Check for tracks per mood
    tracks_per_mood = None
    if '2 tracks per mood' in prompt_lower or 'two tracks per mood' in prompt_lower:
        tracks_per_mood = 2
        print(f"User requested {tracks_per_mood} tracks per mood")
    elif '1 track per mood' in prompt_lower or 'one track per mood' in prompt_lower:
        tracks_per_mood = 1
        print(f"User requested {tracks_per_mood} track per mood")
    elif '3 tracks per mood' in prompt_lower or 'three tracks per mood' in prompt_lower:
        tracks_per_mood = 3
        print(f"User requested {tracks_per_mood} tracks per mood")

    # Parse for custom include/exclude lists
    excluded_artists = []
    included_artists = []

    # Check for artist exclusions
    if 'exclude kendrick' in prompt_lower or 'exclude kendrick lamar' in prompt_lower:
        excluded_artists.append('Kendrick Lamar')
        print("Excluding Kendrick Lamar (except as a feature)")

    if 'exclude xxxtentacion' in prompt_lower or 'exclude xxx' in prompt_lower:
        excluded_artists.append('XXXTENTACION')
        print("Excluding XXXTENTACION")

    # Look for custom exclude list format: "exclude: artist1, artist2, artist3"
    if 'exclude:' in prompt_lower:
        exclude_section = prompt_lower.split('exclude:')[1].split('include:')[0].split('.')[0]
        custom_excludes = [artist.strip() for artist in exclude_section.split(',')]
        for artist in custom_excludes:
            if artist and artist not in excluded_artists:
                # Capitalize each word for proper formatting
                formatted_artist = ' '.join(word.capitalize() for word in artist.split())
                excluded_artists.append(formatted_artist)
                print(f"Custom exclude: {formatted_artist}")

    # Look for custom include list format: "include: artist1, artist2, artist3"
    if 'include:' in prompt_lower:
        include_section = prompt_lower.split('include:')[1].split('exclude:')[0].split('.')[0]
        custom_includes = [artist.strip() for artist in include_section.split(',')]
        for artist in custom_includes:
            if artist:
                # Capitalize each word for proper formatting
                formatted_artist = ' '.join(word.capitalize() for word in artist.split())
                included_artists.append(formatted_artist)
                print(f"Custom include: {formatted_artist}")

    # Extract top artist names for easier reference
    top_artist_names = [artist.get('name', '') for artist in top_artists if artist.get('name') and artist.get('name') not in excluded_artists][:10]

    # Add included artists to the top artists list if they're not already there
    for artist in included_artists:
        if artist not in top_artist_names:
            top_artist_names.append(artist)
            print(f"Added {artist} to top artists list")

    # Shuffle the top artists list for more variety
    random.shuffle(top_artist_names)

    print(f"User's top artists (after exclusions/inclusions): {', '.join(top_artist_names)}")

    # Check if specific artists are mentioned in the prompt
    specific_artists = {}

    # Check for Playboi Carti specifically since it's mentioned in the prompt
    if 'playboi carti' in prompt_lower:
        specific_artists['Playboi Carti'] = {
            'intro': 'walk' in prompt_lower and 'intro' in prompt_lower,
            'finale': 'end' in prompt_lower or 'finally' in prompt_lower
        }

    # Check for other top artists in the prompt
    for artist_name in top_artist_names:
        if artist_name.lower() in prompt_lower and artist_name != 'Playboi Carti':
            specific_artists[artist_name] = {
                'intro': False,  # Only Playboi Carti is specified as intro
                'finale': False  # Only Playboi Carti is specified as finale
            }

    # Create mood categories
    high_energy_tracks = []
    vibey_tracks = []
    melancholic_tracks = []
    sad_tracks = []
    upbeat_tracks = []
    finale_tracks = []

    # Add specific intro track if requested
    intro_track = None
    if specific_artists.get('Playboi Carti', {}).get('intro'):
        intro_track = {
            'name': "WALK",
            'artists': [{'name': "Playboi Carti"}],
            'album': {'name': "WHOLE LOTTA RED"},
            'mood': "high_energy",
            'reason': "Requested as the intro track - high energy opener"
        }

    # Add tracks from top artists to appropriate mood categories
    # This is where we'd use the actual top artists data

    # Check for randomization request
    randomize_selection = 'random' in prompt_lower or 'randomize' in prompt_lower or 'surprise me' in prompt_lower
    if randomize_selection:
        print("User requested randomized track selection")

    # Add Playboi Carti tracks if they're in the top artists
    if 'Playboi Carti' in top_artist_names or 'playboi carti' in prompt_lower:
        # High energy Playboi Carti tracks
        high_energy_tracks.extend([
            {
                'name': "New Tank",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Rage-type track with aggressive delivery"
            },
            {
                'name': "Stop Breathing",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Intense, aggressive track with a hard-hitting beat"
            }
        ])

        # Vibey Playboi Carti tracks
        vibey_tracks.extend([
            {
                'name': "Location",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Playboi Carti"},
                'mood': "vibey",
                'reason': "Ethereal production with ambient qualities"
            },
            {
                'name': "Sky",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "vibey",
                'reason': "More vibey and ambient sound with melodic elements"
            }
        ])

        # Melancholic Playboi Carti tracks
        melancholic_tracks.extend([
            {
                'name': "ILoveUIHateU",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "melancholic",
                'reason': "Melancholic but still energetic with bittersweet lyrics"
            }
        ])

        # Sad Playboi Carti tracks
        sad_tracks.extend([
            {
                'name': "F33l Lik3 Dyin",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "sad",
                'reason': "Emotional outro to Whole Lotta Red with vulnerable lyrics"
            }
        ])

        # Upbeat Playboi Carti tracks
        upbeat_tracks.extend([
            {
                'name': "Magnolia",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Playboi Carti"},
                'mood': "upbeat",
                'reason': "Bouncy and upbeat with an infectious hook"
            },
            {
                'name': "Slay3r",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "upbeat",
                'reason': "Bouncy track with a fun, energetic vibe"
            }
        ])

        # Finale Playboi Carti tracks
        if specific_artists.get('Playboi Carti', {}).get('finale'):
            finale_tracks.extend([
                {
                    'name': "Teen X",
                    'artists': [{'name': "Playboi Carti"}, {'name': "Future"}],
                    'album': {'name': "Whole Lotta Red"},
                    'mood': "high_energy",
                    'reason': "Experimental and high-energy finale that blends multiple styles"
                },
                {
                    'name': "Metamorphosis",
                    'artists': [{'name': "Playboi Carti"}, {'name': "Kid Cudi"}],
                    'album': {'name': "Whole Lotta Red"},
                    'mood': "high_energy",
                    'reason': "Psychedelic track that combines energy with emotional depth - perfect finale"
                }
            ])

    # Add tracks from other top artists
    # We'll add some popular tracks for common top artists

    # Kendrick Lamar - only as a feature if excluded
    if 'Kendrick Lamar' in top_artist_names and 'Kendrick Lamar' not in excluded_artists:
        high_energy_tracks.extend([
            {
                'name': "DNA.",
                'artists': [{'name': "Kendrick Lamar"}],
                'album': {'name': "DAMN."},
                'mood': "high_energy",
                'reason': "Intense lyrics and hard-hitting beat with aggressive delivery"
            },
            {
                'name': "HUMBLE.",
                'artists': [{'name': "Kendrick Lamar"}],
                'album': {'name': "DAMN."},
                'mood': "high_energy",
                'reason': "Confident, assertive track with a powerful beat"
            }
        ])

        melancholic_tracks.extend([
            {
                'name': "PRIDE.",
                'artists': [{'name': "Kendrick Lamar"}],
                'album': {'name': "DAMN."},
                'mood': "melancholic",
                'reason': "Introspective track with a dreamy, nostalgic production"
            }
        ])

        sad_tracks.extend([
            {
                'name': "u",
                'artists': [{'name': "Kendrick Lamar"}],
                'album': {'name': "To Pimp A Butterfly"},
                'mood': "sad",
                'reason': "Intense emotional breakdown with themes of self-loathing and guilt"
            }
        ])

    # Drake
    if 'Drake' in top_artist_names:
        vibey_tracks.extend([
            {
                'name': "Passionfruit",
                'artists': [{'name': "Drake"}],
                'album': {'name': "More Life"},
                'mood': "vibey",
                'reason': "Tropical house-influenced track with a relaxed, groovy feel"
            }
        ])

        sad_tracks.extend([
            {
                'name': "Marvin's Room",
                'artists': [{'name': "Drake"}],
                'album': {'name': "Take Care"},
                'mood': "sad",
                'reason': "Raw emotional vulnerability with drunk phone calls and regret"
            }
        ])

        upbeat_tracks.extend([
            {
                'name': "Nice For What",
                'artists': [{'name': "Drake"}],
                'album': {'name': "Scorpion"},
                'mood': "upbeat",
                'reason': "Bouncy New Orleans bounce-inspired track with an empowering message"
            }
        ])

    # Travis Scott
    if 'Travis Scott' in top_artist_names:
        high_energy_tracks.extend([
            {
                'name': "Sicko Mode",
                'artists': [{'name': "Travis Scott"}, {'name': "Drake"}],
                'album': {'name': "Astroworld"},
                'mood': "high_energy",
                'reason': "High energy track with dynamic beat changes and multiple sections"
            }
        ])

        vibey_tracks.extend([
            {
                'name': "SKELETONS",
                'artists': [{'name': "Travis Scott"}],
                'album': {'name': "Astroworld"},
                'mood': "vibey",
                'reason': "Psychedelic and dreamy production with a hypnotic feel"
            }
        ])

    # Kanye West
    if 'Kanye West' in top_artist_names:
        high_energy_tracks.extend([
            {
                'name': "POWER",
                'artists': [{'name': "Kanye West"}],
                'album': {'name': "My Beautiful Dark Twisted Fantasy"},
                'mood': "high_energy",
                'reason': "Powerful production with energetic delivery"
            }
        ])

        melancholic_tracks.extend([
            {
                'name': "Runaway",
                'artists': [{'name': "Kanye West"}, {'name': "Pusha T"}],
                'album': {'name': "My Beautiful Dark Twisted Fantasy"},
                'mood': "melancholic",
                'reason': "Beautiful piano intro leading to an introspective journey of self-awareness"
            }
        ])

        sad_tracks.extend([
            {
                'name': "Street Lights",
                'artists': [{'name': "Kanye West"}],
                'album': {'name': "808s & Heartbreak"},
                'mood': "sad",
                'reason': "Emotional track with auto-tuned vocals expressing vulnerability"
            }
        ])

        upbeat_tracks.extend([
            {
                'name': "Good Life",
                'artists': [{'name': "Kanye West"}, {'name': "T-Pain"}],
                'album': {'name': "Graduation"},
                'mood': "upbeat",
                'reason': "Celebratory track with a positive message and catchy chorus"
            }
        ])

    # Frank Ocean
    if 'Frank Ocean' in top_artist_names:
        vibey_tracks.extend([
            {
                'name': "Nights",
                'artists': [{'name': "Frank Ocean"}],
                'album': {'name': "Blonde"},
                'mood': "vibey",
                'reason': "Atmospheric with a beat switch that changes the mood halfway through"
            }
        ])

        melancholic_tracks.extend([
            {
                'name': "Self Control",
                'artists': [{'name': "Frank Ocean"}],
                'album': {'name': "Blonde"},
                'mood': "melancholic",
                'reason': "Bittersweet lyrics with beautiful guitar and vocal layering"
            },
            {
                'name': "Ivy",
                'artists': [{'name': "Frank Ocean"}],
                'album': {'name': "Blonde"},
                'mood': "melancholic",
                'reason': "Reflective lyrics about past relationships with a nostalgic tone"
            }
        ])

    # Tyler, The Creator
    if 'Tyler, The Creator' in top_artist_names:
        upbeat_tracks.extend([
            {
                'name': "EARFQUAKE",
                'artists': [{'name': "Tyler, The Creator"}],
                'album': {'name': "IGOR"},
                'mood': "upbeat",
                'reason': "Bouncy track with a catchy chorus and playful energy"
            }
        ])

        melancholic_tracks.extend([
            {
                'name': "See You Again",
                'artists': [{'name': "Tyler, The Creator"}, {'name': "Kali Uchis"}],
                'album': {'name': "Flower Boy"},
                'mood': "melancholic",
                'reason': "Dreamy production with nostalgic lyrics about longing"
            }
        ])

    # The Weeknd
    if 'The Weeknd' in top_artist_names:
        vibey_tracks.extend([
            {
                'name': "After Hours",
                'artists': [{'name': "The Weeknd"}],
                'album': {'name': "After Hours"},
                'mood': "vibey",
                'reason': "Ambient production with a hypnotic rhythm and nocturnal feel"
            }
        ])

        upbeat_tracks.extend([
            {
                'name': "Blinding Lights",
                'artists': [{'name': "The Weeknd"}],
                'album': {'name': "After Hours"},
                'mood': "upbeat",
                'reason': "Energetic 80s-inspired synth-pop track with a driving beat"
            }
        ])

    # Add more artists as needed...

    # If we don't have enough tracks from the user's top artists, add some generic ones
    if len(high_energy_tracks) < 3:
        high_energy_tracks.extend([
            {
                'name': "Mo Bamba",
                'artists': [{'name': "Sheck Wes"}],
                'album': {'name': "Mudboy"},
                'mood': "high_energy",
                'reason': "Rage-inducing anthem with heavy bass and crowd-pleasing energy"
            }
        ])

    if len(vibey_tracks) < 3:
        vibey_tracks.extend([
            {
                'name': "Redbone",
                'artists': [{'name': "Childish Gambino"}],
                'album': {'name': "Awaken, My Love!"},
                'mood': "vibey",
                'reason': "Smooth, funk-inspired groove with atmospheric production"
            }
        ])

    if len(melancholic_tracks) < 3:
        melancholic_tracks.extend([
            {
                'name': "505",
                'artists': [{'name': "Arctic Monkeys"}],
                'album': {'name': "Favourite Worst Nightmare"},
                'mood': "melancholic",
                'reason': "Nostalgic and builds to an emotional climax with yearning lyrics"
            }
        ])

    if len(sad_tracks) < 3 and 'XXXTENTACION' not in excluded_artists:
        sad_tracks.extend([
            {
                'name': "Jocelyn Flores",
                'artists': [{'name': "XXXTENTACION"}],
                'album': {'name': "17"},
                'mood': "sad",
                'reason': "Deeply emotional tribute to a friend who passed away"
            }
        ])
    elif len(sad_tracks) < 3:
        # Alternative sad track if XXXTENTACION is excluded
        sad_tracks.extend([
            {
                'name': "Hurt",
                'artists': [{'name': "Johnny Cash"}],
                'album': {'name': "American IV: The Man Comes Around"},
                'mood': "sad",
                'reason': "Powerful cover filled with regret and reflection"
            }
        ])

    if len(upbeat_tracks) < 3:
        upbeat_tracks.extend([
            {
                'name': "Sunflower",
                'artists': [{'name': "Post Malone"}, {'name': "Swae Lee"}],
                'album': {'name': "Spider-Man: Into the Spider-Verse"},
                'mood': "upbeat",
                'reason': "Bright melody with uplifting lyrics and a catchy chorus"
            }
        ])

    if len(finale_tracks) < 1 and 'end' in prompt_lower:
        finale_tracks.extend([
            {
                'name': "Stronger",
                'artists': [{'name': "Kanye West"}],
                'album': {'name': "Graduation"},
                'mood': "high_energy",
                'reason': "Triumphant finale that combines electronic elements with motivational themes"
            }
        ])

    # Combine all tracks to create a complete journey with some randomization
    journey = []

    # Add the specific intro track if requested
    if intro_track:
        journey.append(intro_track)

    # Shuffle each mood category to add variety
    # but keep the overall journey structure intact
    # If randomize_selection is true, we'll do a more thorough shuffle
    if randomize_selection:
        # For a more randomized experience, we'll shuffle multiple times
        for _ in range(3):
            random.shuffle(high_energy_tracks)
            random.shuffle(vibey_tracks)
            random.shuffle(melancholic_tracks)
            random.shuffle(sad_tracks)
            random.shuffle(upbeat_tracks)
        print("Applied extra randomization to track selection")
    else:
        # Standard shuffle for normal variety
        random.shuffle(high_energy_tracks)
        random.shuffle(vibey_tracks)
        random.shuffle(melancholic_tracks)
        random.shuffle(sad_tracks)
        random.shuffle(upbeat_tracks)

    # Check for different outro request
    different_outro = 'different outro' in prompt_lower

    # Check for custom track requests
    custom_track_requests = []
    if 'add track:' in prompt_lower or 'add song:' in prompt_lower:
        # Extract custom track requests
        track_sections = []
        if 'add track:' in prompt_lower:
            track_sections.extend(prompt_lower.split('add track:')[1:])
        if 'add song:' in prompt_lower:
            track_sections.extend(prompt_lower.split('add song:')[1:])

        for section in track_sections:
            # Extract the track info up to the next keyword or end of text
            track_info = section.split('add')[0].strip()
            if not track_info.endswith('.'):
                track_info = track_info.split('.')[0]

            # Try to parse artist and song
            if ' by ' in track_info:
                song, artist = track_info.split(' by ', 1)
                song = song.strip()
                artist = artist.strip()

                # Format properly
                artist = ' '.join(word.capitalize() for word in artist.split())

                # Add to custom tracks
                custom_track = {
                    'name': song,
                    'artists': [{'name': artist}],
                    'album': {'name': "Unknown"},
                    'mood': "custom",
                    'reason': "User specifically requested this track"
                }
                custom_track_requests.append(custom_track)
                print(f"Adding custom track: {song} by {artist}")

    # Add custom tracks to the journey
    if custom_track_requests:
        # Insert custom tracks at the beginning of the journey
        for track in custom_track_requests:
            journey.append(track)
        # Reduce the track limit to account for custom tracks
        track_limit -= len(custom_track_requests)

    if different_outro and 'Playboi Carti' in specific_artists:
        print("User requested a different outro than Playboi Carti")
        # Replace the finale tracks with something else
        if 'Kanye West' in top_artist_names:
            finale_tracks = [{
                'name': "Stronger",
                'artists': [{'name': "Kanye West"}],
                'album': {'name': "Graduation"},
                'mood': "high_energy",
                'reason': "Triumphant finale that combines electronic elements with motivational themes"
            }]
        elif 'Travis Scott' in top_artist_names:
            finale_tracks = [{
                'name': "STARGAZING",
                'artists': [{'name': "Travis Scott"}],
                'album': {'name': "Astroworld"},
                'mood': "high_energy",
                'reason': "Psychedelic track with a beat switch that serves as a perfect finale"
            }]
        elif 'Drake' in top_artist_names:
            finale_tracks = [{
                'name': "Headlines",
                'artists': [{'name': "Drake"}],
                'album': {'name': "Take Care"},
                'mood': "high_energy",
                'reason': "Confident track with a triumphant feel that works well as a finale"
            }]
        else:
            finale_tracks = [{
                'name': "Stronger",
                'artists': [{'name': "Kanye West"}],
                'album': {'name': "Graduation"},
                'mood': "high_energy",
                'reason': "Triumphant finale that combines electronic elements with motivational themes"
            }]

    # Create a balanced journey with the requested number of tracks
    # We'll allocate tracks proportionally to each mood
    journey = []

    # Add the specific intro track if requested
    if intro_track:
        journey.append(intro_track)
        track_limit -= 1  # Reduce the limit since we've added the intro

    # Check for custom mood weights in the prompt
    mood_weights = {
        'high_energy': 1,
        'vibey': 1,
        'melancholic': 1,
        'sad': 1,
        'upbeat': 1
    }

    # Look for phrases like "more high energy" or "less sad"
    if 'more high energy' in prompt_lower or 'extra high energy' in prompt_lower:
        mood_weights['high_energy'] = 2
        print("Increasing weight for high energy tracks")
    if 'more vibey' in prompt_lower or 'extra vibey' in prompt_lower:
        mood_weights['vibey'] = 2
        print("Increasing weight for vibey tracks")
    if 'more melancholic' in prompt_lower or 'extra melancholic' in prompt_lower:
        mood_weights['melancholic'] = 2
        print("Increasing weight for melancholic tracks")
    if 'more sad' in prompt_lower or 'extra sad' in prompt_lower:
        mood_weights['sad'] = 2
        print("Increasing weight for sad tracks")
    if 'more upbeat' in prompt_lower or 'extra upbeat' in prompt_lower:
        mood_weights['upbeat'] = 2
        print("Increasing weight for upbeat tracks")

    if 'less high energy' in prompt_lower or 'fewer high energy' in prompt_lower:
        mood_weights['high_energy'] = 0.5
        print("Decreasing weight for high energy tracks")
    if 'less vibey' in prompt_lower or 'fewer vibey' in prompt_lower:
        mood_weights['vibey'] = 0.5
        print("Decreasing weight for vibey tracks")
    if 'less melancholic' in prompt_lower or 'fewer melancholic' in prompt_lower:
        mood_weights['melancholic'] = 0.5
        print("Decreasing weight for melancholic tracks")
    if 'less sad' in prompt_lower or 'fewer sad' in prompt_lower:
        mood_weights['sad'] = 0.5
        print("Decreasing weight for sad tracks")
    if 'less upbeat' in prompt_lower or 'fewer upbeat' in prompt_lower:
        mood_weights['upbeat'] = 0.5
        print("Decreasing weight for upbeat tracks")

    # Calculate how many tracks to include from each mood category
    # We want to maintain the emotional journey while respecting the track limit
    remaining_tracks = track_limit - len(finale_tracks)

    # If tracks_per_mood was specified in the prompt, use that instead of calculating
    if tracks_per_mood is not None:
        # Override the calculated values with the user-specified value
        tracks_per_mood = {
            'high_energy': tracks_per_mood,
            'vibey': tracks_per_mood,
            'melancholic': tracks_per_mood,
            'sad': tracks_per_mood,
            'upbeat': tracks_per_mood
        }
        print(f"Using {tracks_per_mood['high_energy']} tracks per mood as requested")
    else:
        # Calculate total weight
        total_weight = sum(mood_weights.values())

        # Calculate tracks per mood based on weights
        tracks_per_mood = {}
        for mood, weight in mood_weights.items():
            # Calculate proportional number of tracks for this mood
            mood_tracks = max(1, int(remaining_tracks * (weight / total_weight)))
            tracks_per_mood[mood] = mood_tracks

    # Adjust if we've allocated too many tracks
    total_allocated = sum(tracks_per_mood.values())
    if total_allocated > remaining_tracks:
        # Remove tracks from moods with the most tracks
        sorted_moods = sorted(tracks_per_mood.items(), key=lambda x: x[1], reverse=True)
        for mood, _ in sorted_moods:
            if total_allocated <= remaining_tracks:
                break
            if tracks_per_mood[mood] > 1:
                tracks_per_mood[mood] -= 1
                total_allocated -= 1

    # Add tracks from each mood category based on calculated weights
    print(f"Track allocation: {tracks_per_mood}")
    journey.extend(high_energy_tracks[:tracks_per_mood['high_energy']])
    journey.extend(vibey_tracks[:tracks_per_mood['vibey']])
    journey.extend(melancholic_tracks[:tracks_per_mood['melancholic']])
    journey.extend(sad_tracks[:tracks_per_mood['sad']])
    journey.extend(upbeat_tracks[:tracks_per_mood['upbeat']])

    # If we still have room, add some random tracks from any category
    remaining = track_limit - len(journey) - len(finale_tracks)
    if remaining > 0:
        print(f"Adding {remaining} additional tracks to fill the playlist")
        # Combine all remaining tracks
        remaining_tracks_pool = []
        remaining_tracks_pool.extend(high_energy_tracks[tracks_per_mood['high_energy']:])
        remaining_tracks_pool.extend(vibey_tracks[tracks_per_mood['vibey']:])
        remaining_tracks_pool.extend(melancholic_tracks[tracks_per_mood['melancholic']:])
        remaining_tracks_pool.extend(sad_tracks[tracks_per_mood['sad']:])
        remaining_tracks_pool.extend(upbeat_tracks[tracks_per_mood['upbeat']:])

        # Shuffle and add remaining tracks
        random.shuffle(remaining_tracks_pool)
        journey.extend(remaining_tracks_pool[:remaining])

    # Add the finale tracks
    journey.extend(finale_tracks)

    return journey

def fallback_recommendations(prompt):
    """Provide fallback recommendations if the AI service fails"""
    print("Using fallback recommendations")

    # Use random to add some variety to the recommendations
    # This ensures we don't always return the exact same tracks in the same order
    random.seed(hash(prompt) % 10000)  # Use the prompt to seed the random generator

    # Check for specific artist mentions and request patterns
    prompt_lower = prompt.lower()

    # Check if this is a request for a mixed artist journey with a specific intro track
    mixed_artist_journey = 'top artists' in prompt_lower and 'journey' in prompt_lower
    specific_intro = False

    # Check for specific intro track requests
    if 'walk' in prompt_lower and 'playboi carti' in prompt_lower and 'intro' in prompt_lower:
        specific_intro = True
        print("Detected request for WALK by Playboi Carti as intro with mixed artists journey")

    # Pure Playboi Carti journey (only if not requesting mixed artists)
    if 'playboi carti' in prompt_lower and not mixed_artist_journey:
        # Create a comprehensive Playboi Carti journey
        high_energy_tracks = [
            {
                'name': "WALK",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "WHOLE LOTTA RED"},
                'mood': "high_energy",
                'reason': "Requested as the intro track - high energy opener"
            },
            {
                'name': "New Tank",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "High energy, rage-type track with aggressive delivery"
            },
            {
                'name': "Stop Breathing",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Intense, aggressive track with a hard-hitting beat"
            },
            {
                'name': "R.I.P.",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Die Lit"},
                'mood': "high_energy",
                'reason': "Mosh pit energy with punk-inspired production"
            }
        ]

        vibey_tracks = [
            {
                'name': "Sky",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "vibey",
                'reason': "More vibey and ambient sound with melodic elements"
            },
            {
                'name': "Place",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "vibey",
                'reason': "Spacey production with a relaxed flow"
            },
            {
                'name': "Flex",
                'artists': [{'name': "Playboi Carti"}, {'name': "Leven Kali"}],
                'album': {'name': "Playboi Carti"},
                'mood': "vibey",
                'reason': "Smooth, laid-back track with dreamy production"
            },
            {
                'name': "Location",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Playboi Carti"},
                'mood': "vibey",
                'reason': "Ethereal production with ambient qualities"
            }
        ]

        melancholic_tracks = [
            {
                'name': "ILoveUIHateU",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "melancholic",
                'reason': "Melancholic but still energetic with bittersweet lyrics"
            },
            {
                'name': "Over",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "melancholic",
                'reason': "Reflective track with a nostalgic feel"
            },
            {
                'name': "Fell In Luv",
                'artists': [{'name': "Playboi Carti"}, {'name': "Bryson Tiller"}],
                'album': {'name': "Die Lit"},
                'mood': "melancholic",
                'reason': "Emotional track about love with a dreamy beat"
            }
        ]

        sad_tracks = [
            {
                'name': "Long Time (Intro)",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Die Lit"},
                'mood': "sad",
                'reason': "Emotional and reflective with introspective lyrics"
            },
            {
                'name': "F33l Lik3 Dyin",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "sad",
                'reason': "Emotional outro to Whole Lotta Red with vulnerable lyrics"
            },
            {
                'name': "Control",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "sad",
                'reason': "Emotional track with themes of love and vulnerability"
            }
        ]

        upbeat_tracks = [
            {
                'name': "Magnolia",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Playboi Carti"},
                'mood': "upbeat",
                'reason': "Bouncy and upbeat with an infectious hook"
            },
            {
                'name': "Shoota",
                'artists': [{'name': "Playboi Carti"}, {'name': "Lil Uzi Vert"}],
                'album': {'name': "Die Lit"},
                'mood': "upbeat",
                'reason': "Energetic collaboration with a playful vibe"
            },
            {
                'name': "wokeuplikethis*",
                'artists': [{'name': "Playboi Carti"}, {'name': "Lil Uzi Vert"}],
                'album': {'name': "Playboi Carti"},
                'mood': "upbeat",
                'reason': "Upbeat track with a catchy melody"
            },
            {
                'name': "Slay3r",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "upbeat",
                'reason': "Bouncy track with a fun, energetic vibe"
            }
        ]

        finale_tracks = [
            {
                'name': "Teen X",
                'artists': [{'name': "Playboi Carti"}, {'name': "Future"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Experimental and high-energy finale that blends multiple styles"
            },
            {
                'name': "Metamorphosis",
                'artists': [{'name': "Playboi Carti"}, {'name': "Kid Cudi"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Psychedelic track that combines energy with emotional depth"
            }
        ]

        # Combine all tracks to create a complete journey with some randomization
        journey = []

        # Shuffle each mood category slightly to add variety
        # but keep the overall journey structure intact
        random.shuffle(high_energy_tracks)
        random.shuffle(vibey_tracks)
        random.shuffle(melancholic_tracks)
        random.shuffle(sad_tracks)
        random.shuffle(upbeat_tracks)

        # Make sure WALK is always the first track if it's in the prompt
        if 'walk' in prompt_lower:
            walk_track = None
            for track in high_energy_tracks:
                if track['name'].lower() == 'walk':
                    walk_track = track
                    high_energy_tracks.remove(track)
                    break

            if walk_track:
                journey.append(walk_track)

        # Add tracks to the journey
        journey.extend(high_energy_tracks)
        journey.extend(vibey_tracks)
        journey.extend(melancholic_tracks)
        journey.extend(sad_tracks)
        journey.extend(upbeat_tracks)
        journey.extend(finale_tracks)

        return journey

    # Mixed artist journey with specific intro track
    if mixed_artist_journey or specific_intro:
        print("Creating mixed artist journey with top artists")

        # Create a diverse journey with various artists
        # Start with WALK by Playboi Carti if specifically requested
        intro_track = None
        if specific_intro:
            intro_track = {
                'name': "WALK",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "WHOLE LOTTA RED"},
                'mood': "high_energy",
                'reason': "Requested as the intro track - high energy opener"
            }

        # Create a diverse set of high energy tracks by different artists
        high_energy_tracks = [
            {
                'name': "Sicko Mode",
                'artists': [{'name': "Travis Scott"}, {'name': "Drake"}],
                'album': {'name': "Astroworld"},
                'mood': "high_energy",
                'reason': "High energy track with dynamic beat changes and multiple sections"
            },
            {
                'name': "DNA.",
                'artists': [{'name': "Kendrick Lamar"}],
                'album': {'name': "DAMN."},
                'mood': "high_energy",
                'reason': "Intense lyrics and hard-hitting beat with aggressive delivery"
            },
            {
                'name': "New Tank",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Rage-type track with aggressive delivery"
            },
            {
                'name': "POWER",
                'artists': [{'name': "Kanye West"}],
                'album': {'name': "My Beautiful Dark Twisted Fantasy"},
                'mood': "high_energy",
                'reason': "Powerful production with energetic delivery"
            },
            {
                'name': "m.A.A.d city",
                'artists': [{'name': "Kendrick Lamar"}, {'name': "MC Eiht"}],
                'album': {'name': "good kid, m.A.A.d city"},
                'mood': "high_energy",
                'reason': "Intense storytelling with a hard-hitting beat"
            }
        ]

        # Vibey and ambient tracks by different artists
        vibey_tracks = [
            {
                'name': "Nights",
                'artists': [{'name': "Frank Ocean"}],
                'album': {'name': "Blonde"},
                'mood': "vibey",
                'reason': "Atmospheric with a beat switch that changes the mood halfway through"
            },
            {
                'name': "Location",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Playboi Carti"},
                'mood': "vibey",
                'reason': "Ethereal production with ambient qualities"
            },
            {
                'name': "Redbone",
                'artists': [{'name': "Childish Gambino"}],
                'album': {'name': "Awaken, My Love!"},
                'mood': "vibey",
                'reason': "Smooth, funk-inspired groove with atmospheric production"
            },
            {
                'name': "After Hours",
                'artists': [{'name': "The Weeknd"}],
                'album': {'name': "After Hours"},
                'mood': "vibey",
                'reason': "Ambient production with a hypnotic rhythm and nocturnal feel"
            },
            {
                'name': "Flashing Lights",
                'artists': [{'name': "Kanye West"}, {'name': "Dwele"}],
                'album': {'name': "Graduation"},
                'mood': "vibey",
                'reason': "Lush production with strings and synths creating an immersive atmosphere"
            }
        ]

        # Melancholic but beautiful tracks by different artists
        melancholic_tracks = [
            {
                'name': "Self Control",
                'artists': [{'name': "Frank Ocean"}],
                'album': {'name': "Blonde"},
                'mood': "melancholic",
                'reason': "Bittersweet lyrics with beautiful guitar and vocal layering"
            },
            {
                'name': "ILoveUIHateU",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "melancholic",
                'reason': "Melancholic but still energetic with bittersweet lyrics"
            },
            {
                'name': "Runaway",
                'artists': [{'name': "Kanye West"}, {'name': "Pusha T"}],
                'album': {'name': "My Beautiful Dark Twisted Fantasy"},
                'mood': "melancholic",
                'reason': "Beautiful piano intro leading to an introspective journey of self-awareness"
            },
            {
                'name': "Ivy",
                'artists': [{'name': "Frank Ocean"}],
                'album': {'name': "Blonde"},
                'mood': "melancholic",
                'reason': "Reflective lyrics about past relationships with a nostalgic tone"
            },
            {
                'name': "505",
                'artists': [{'name': "Arctic Monkeys"}],
                'album': {'name': "Favourite Worst Nightmare"},
                'mood': "melancholic",
                'reason': "Nostalgic and builds to an emotional climax with yearning lyrics"
            }
        ]

        # Sad and emotional tracks by different artists
        sad_tracks = [
            {
                'name': "Marvin's Room",
                'artists': [{'name': "Drake"}],
                'album': {'name': "Take Care"},
                'mood': "sad",
                'reason': "Raw emotional vulnerability with drunk phone calls and regret"
            },
            {
                'name': "F33l Lik3 Dyin",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "sad",
                'reason': "Emotional outro to Whole Lotta Red with vulnerable lyrics"
            },
            {
                'name': "u",
                'artists': [{'name': "Kendrick Lamar"}],
                'album': {'name': "To Pimp A Butterfly"},
                'mood': "sad",
                'reason': "Intense emotional breakdown with themes of self-loathing and guilt"
            },
            {
                'name': "Jocelyn Flores",
                'artists': [{'name': "XXXTENTACION"}],
                'album': {'name': "17"},
                'mood': "sad",
                'reason': "Deeply emotional tribute to a friend who passed away"
            },
            {
                'name': "Street Lights",
                'artists': [{'name': "Kanye West"}],
                'album': {'name': "808s & Heartbreak"},
                'mood': "sad",
                'reason': "Emotional track with auto-tuned vocals expressing vulnerability"
            }
        ]

        # Upbeat and bouncy tracks by different artists
        upbeat_tracks = [
            {
                'name': "Magnolia",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Playboi Carti"},
                'mood': "upbeat",
                'reason': "Bouncy and upbeat with an infectious hook"
            },
            {
                'name': "Good Life",
                'artists': [{'name': "Kanye West"}, {'name': "T-Pain"}],
                'album': {'name': "Graduation"},
                'mood': "upbeat",
                'reason': "Celebratory track with a positive message and catchy chorus"
            },
            {
                'name': "Sunflower",
                'artists': [{'name': "Post Malone"}, {'name': "Swae Lee"}],
                'album': {'name': "Spider-Man: Into the Spider-Verse"},
                'mood': "upbeat",
                'reason': "Bright melody with uplifting lyrics and a catchy chorus"
            },
            {
                'name': "EARFQUAKE",
                'artists': [{'name': "Tyler, The Creator"}],
                'album': {'name': "IGOR"},
                'mood': "upbeat",
                'reason': "Bouncy track with a catchy chorus and playful energy"
            },
            {
                'name': "Slay3r",
                'artists': [{'name': "Playboi Carti"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "upbeat",
                'reason': "Bouncy track with a fun, energetic vibe"
            }
        ]

        # Finale tracks - end with a Playboi Carti song that blends all moods
        finale_tracks = [
            {
                'name': "Teen X",
                'artists': [{'name': "Playboi Carti"}, {'name': "Future"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Experimental and high-energy finale that blends multiple styles"
            },
            {
                'name': "Metamorphosis",
                'artists': [{'name': "Playboi Carti"}, {'name': "Kid Cudi"}],
                'album': {'name': "Whole Lotta Red"},
                'mood': "high_energy",
                'reason': "Psychedelic track that combines energy with emotional depth - perfect finale"
            }
        ]

        # Combine all tracks to create a complete journey with some randomization
        journey = []

        # Add the specific intro track if requested
        if intro_track:
            journey.append(intro_track)

        # Shuffle each mood category slightly to add variety
        # but keep the overall journey structure intact
        random.shuffle(high_energy_tracks)
        random.shuffle(vibey_tracks)
        random.shuffle(melancholic_tracks)
        random.shuffle(sad_tracks)
        random.shuffle(upbeat_tracks)

        # Add tracks to the journey
        journey.extend(high_energy_tracks)
        journey.extend(vibey_tracks)
        journey.extend(melancholic_tracks)
        journey.extend(sad_tracks)
        journey.extend(upbeat_tracks)
        journey.extend(finale_tracks)

        return journey

    # Generic recommendations based on mood journey
    high_energy_tracks = [
        {
            'name': "Sicko Mode",
            'artists': [{'name': "Travis Scott"}, {'name': "Drake"}],
            'album': {'name': "Astroworld"},
            'mood': "high_energy",
            'reason': "High energy opener with dynamic beat changes and multiple sections"
        },
        {
            'name': "DNA.",
            'artists': [{'name': "Kendrick Lamar"}],
            'album': {'name': "DAMN."},
            'mood': "high_energy",
            'reason': "Intense lyrics and hard-hitting beat with aggressive delivery"
        },
        {
            'name': "Mo Bamba",
            'artists': [{'name': "Sheck Wes"}],
            'album': {'name': "Mudboy"},
            'mood': "high_energy",
            'reason': "Rage-inducing anthem with heavy bass and crowd-pleasing energy"
        },
        {
            'name': "HUMBLE.",
            'artists': [{'name': "Kendrick Lamar"}],
            'album': {'name': "DAMN."},
            'mood': "high_energy",
            'reason': "Confident, assertive track with a powerful beat"
        },
        {
            'name': "Goosebumps",
            'artists': [{'name': "Travis Scott"}, {'name': "Kendrick Lamar"}],
            'album': {'name': "Birds in the Trap Sing McKnight"},
            'mood': "high_energy",
            'reason': "Hypnotic, high-energy track with psychedelic elements"
        }
    ]

    vibey_tracks = [
        {
            'name': "Redbone",
            'artists': [{'name': "Childish Gambino"}],
            'album': {'name': "Awaken, My Love!"},
            'mood': "vibey",
            'reason': "Smooth, funk-inspired groove with atmospheric production"
        },
        {
            'name': "Nights",
            'artists': [{'name': "Frank Ocean"}],
            'album': {'name': "Blonde"},
            'mood': "vibey",
            'reason': "Atmospheric with a beat switch that changes the mood halfway through"
        },
        {
            'name': "After Hours",
            'artists': [{'name': "The Weeknd"}],
            'album': {'name': "After Hours"},
            'mood': "vibey",
            'reason': "Ambient production with a hypnotic rhythm and nocturnal feel"
        },
        {
            'name': "Passionfruit",
            'artists': [{'name': "Drake"}],
            'album': {'name': "More Life"},
            'mood': "vibey",
            'reason': "Tropical house-influenced track with a relaxed, groovy feel"
        },
        {
            'name': "Flashing Lights",
            'artists': [{'name': "Kanye West"}, {'name': "Dwele"}],
            'album': {'name': "Graduation"},
            'mood': "vibey",
            'reason': "Lush production with strings and synths creating an immersive atmosphere"
        }
    ]

    melancholic_tracks = [
        {
            'name': "Self Control",
            'artists': [{'name': "Frank Ocean"}],
            'album': {'name': "Blonde"},
            'mood': "melancholic",
            'reason': "Bittersweet lyrics with beautiful guitar and vocal layering"
        },
        {
            'name': "505",
            'artists': [{'name': "Arctic Monkeys"}],
            'album': {'name': "Favourite Worst Nightmare"},
            'mood': "melancholic",
            'reason': "Nostalgic and builds to an emotional climax with yearning lyrics"
        },
        {
            'name': "Ivy",
            'artists': [{'name': "Frank Ocean"}],
            'album': {'name': "Blonde"},
            'mood': "melancholic",
            'reason': "Reflective lyrics about past relationships with a nostalgic tone"
        },
        {
            'name': "Runaway",
            'artists': [{'name': "Kanye West"}, {'name': "Pusha T"}],
            'album': {'name': "My Beautiful Dark Twisted Fantasy"},
            'mood': "melancholic",
            'reason': "Beautiful piano intro leading to an introspective journey of self-awareness"
        },
        {
            'name': "Mirrors",
            'artists': [{'name': "Justin Timberlake"}],
            'album': {'name': "The 20/20 Experience"},
            'mood': "melancholic",
            'reason': "Reflective lyrics with a bittersweet melody and expansive production"
        }
    ]

    sad_tracks = [
        {
            'name': "Marvin's Room",
            'artists': [{'name': "Drake"}],
            'album': {'name': "Take Care"},
            'mood': "sad",
            'reason': "Raw emotional vulnerability with drunk phone calls and regret"
        },
        {
            'name': "Jocelyn Flores",
            'artists': [{'name': "XXXTENTACION"}],
            'album': {'name': "17"},
            'mood': "sad",
            'reason': "Deeply emotional tribute to a friend who passed away"
        },
        {
            'name': "u",
            'artists': [{'name': "Kendrick Lamar"}],
            'album': {'name': "To Pimp A Butterfly"},
            'mood': "sad",
            'reason': "Intense emotional breakdown with themes of self-loathing and guilt"
        },
        {
            'name': "Hurt",
            'artists': [{'name': "Johnny Cash"}],
            'album': {'name': "American IV: The Man Comes Around"},
            'mood': "sad",
            'reason': "Powerful cover filled with regret and reflection at the end of life"
        },
        {
            'name': "Everybody Hurts",
            'artists': [{'name': "R.E.M."}],
            'album': {'name': "Automatic for the People"},
            'mood': "sad",
            'reason': "Universal anthem about pain and the importance of perseverance"
        }
    ]

    upbeat_tracks = [
        {
            'name': "Sunflower",
            'artists': [{'name': "Post Malone"}, {'name': "Swae Lee"}],
            'album': {'name': "Spider-Man: Into the Spider-Verse"},
            'mood': "upbeat",
            'reason': "Bright melody with uplifting lyrics and a catchy chorus"
        },
        {
            'name': "Good Feeling",
            'artists': [{'name': "Flo Rida"}],
            'album': {'name': "Wild Ones"},
            'mood': "upbeat",
            'reason': "Energetic dance track with positive vibes and motivational lyrics"
        },
        {
            'name': "I Wanna Dance With Somebody",
            'artists': [{'name': "Whitney Houston"}],
            'album': {'name': "Whitney"},
            'mood': "upbeat",
            'reason': "Classic feel-good dance anthem with joyful energy"
        },
        {
            'name': "Can't Stop the Feeling!",
            'artists': [{'name': "Justin Timberlake"}],
            'album': {'name': "Trolls (Original Motion Picture Soundtrack)"},
            'mood': "upbeat",
            'reason': "Infectious pop song designed to make people dance and feel good"
        },
        {
            'name': "Uptown Funk",
            'artists': [{'name': "Mark Ronson"}, {'name': "Bruno Mars"}],
            'album': {'name': "Uptown Special"},
            'mood': "upbeat",
            'reason': "Funk-inspired hit with irresistible groove and confident energy"
        }
    ]

    finale_tracks = [
        {
            'name': "Stronger",
            'artists': [{'name': "Kanye West"}],
            'album': {'name': "Graduation"},
            'mood': "high_energy",
            'reason': "Triumphant finale that combines electronic elements with motivational themes"
        },
        {
            'name': "All of the Lights",
            'artists': [{'name': "Kanye West"}, {'name': "Rihanna"}, {'name': "Kid Cudi"}],
            'album': {'name': "My Beautiful Dark Twisted Fantasy"},
            'mood': "high_energy",
            'reason': "Grand, orchestral production that brings together multiple elements for an epic conclusion"
        }
    ]

    # Combine tracks to create a journey, with some randomization
    journey = []

    # Shuffle each mood category slightly to add variety
    # but keep the overall journey structure intact
    random.shuffle(high_energy_tracks)
    random.shuffle(vibey_tracks)
    random.shuffle(melancholic_tracks)
    random.shuffle(sad_tracks)
    random.shuffle(upbeat_tracks)

    # Add tracks to the journey
    journey.extend(high_energy_tracks)
    journey.extend(vibey_tracks)
    journey.extend(melancholic_tracks)
    journey.extend(sad_tracks)
    journey.extend(upbeat_tracks)
    journey.extend(finale_tracks)

    return journey
