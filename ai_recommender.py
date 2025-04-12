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

def fallback_recommendations(prompt):
    """Provide fallback recommendations if the AI service fails"""
    print("Using fallback recommendations")

    # Use random to add some variety to the recommendations
    # This ensures we don't always return the exact same tracks in the same order
    random.seed(hash(prompt) % 10000)  # Use the prompt to seed the random generator

    # Check for specific artist mentions
    prompt_lower = prompt.lower()

    # Playboi Carti specific recommendations
    if 'playboi carti' in prompt_lower:
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
