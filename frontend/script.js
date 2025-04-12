document.addEventListener('DOMContentLoaded', () => {
    // This will work with both local development and production
    // For production, replace with your actual Render URL
    const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? '' // Use relative URL for local development
        : 'https://spotify-playlist-creator-1a7x.onrender.com'; // Your actual Render URL
    let accessToken = null;

    // Check if we have an access token in the URL (after redirect)
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    accessToken = hashParams.get('access_token');

    // Show the app section by default for the demo
    showApp();

    if (accessToken) {
        // Remove the access token from URL for security
        window.history.replaceState({}, document.title, window.location.pathname);
        // Show user profile and load Spotify data if logged in
        document.getElementById('user-profile').classList.remove('hidden');
        loadUserProfile();
        loadTopArtists();
        loadTopTracks();
    } else {
        // Show login section but keep app section visible for demo
        document.getElementById('login-section').classList.remove('hidden');
    }

    // Event Listeners
    document.getElementById('login-button').addEventListener('click', login);
    document.getElementById('create-playlist-button').addEventListener('click', createPlaylist);

    // Functions
    function login() {
        fetch(`${API_BASE_URL}/login`)
            .then(response => response.json())
            .then(data => {
                window.location.href = data.auth_url;
            })
            .catch(error => console.error('Error:', error));
    }

    function showLogin() {
        document.getElementById('login-section').classList.remove('hidden');
        document.getElementById('app-section').classList.add('hidden');
        document.getElementById('user-profile').classList.add('hidden');
    }

    function showApp() {
        // For the demo, we show the app section but don't hide the login section
        document.getElementById('app-section').classList.remove('hidden');
        // User profile is only shown when logged in
    }

    function loadUserProfile() {
        fetch(`${API_BASE_URL}/user-profile?access_token=${accessToken}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('profile-name').textContent = data.display_name;
                if (data.images && data.images.length > 0) {
                    document.getElementById('profile-image').src = data.images[0].url;
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function loadTopArtists() {
        fetch(`${API_BASE_URL}/top-artists?access_token=${accessToken}`)
            .then(response => response.json())
            .then(data => {
                const artistsContainer = document.getElementById('top-artists');
                artistsContainer.innerHTML = '';

                data.items.forEach(artist => {
                    const artistCard = document.createElement('div');
                    artistCard.className = 'artist-card';

                    const artistImage = artist.images && artist.images.length > 0
                        ? artist.images[0].url
                        : 'https://via.placeholder.com/150';

                    artistCard.innerHTML = `
                        <img src="${artistImage}" alt="${artist.name}">
                        <div class="card-info">
                            <h3>${artist.name}</h3>
                        </div>
                    `;

                    artistsContainer.appendChild(artistCard);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    function loadTopTracks() {
        fetch(`${API_BASE_URL}/top-tracks?access_token=${accessToken}`)
            .then(response => response.json())
            .then(data => {
                const tracksContainer = document.getElementById('top-tracks');
                tracksContainer.innerHTML = '';

                data.items.forEach(track => {
                    const trackCard = document.createElement('div');
                    trackCard.className = 'track-card';

                    const albumImage = track.album.images && track.album.images.length > 0
                        ? track.album.images[0].url
                        : 'https://via.placeholder.com/150';

                    trackCard.innerHTML = `
                        <img src="${albumImage}" alt="${track.name}">
                        <div class="card-info">
                            <h3>${track.name}</h3>
                            <p>${track.artists[0].name}</p>
                        </div>
                    `;

                    tracksContainer.appendChild(trackCard);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    function createPlaylist() {
        const prompt = document.getElementById('playlist-prompt').value;
        if (!prompt) {
            alert('Please enter a description for your recommendations');
            return;
        }

        const createButton = document.getElementById('create-playlist-button');
        createButton.textContent = 'Creating Journey...';
        createButton.disabled = true;

        fetch(`${API_BASE_URL}/create-journey`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                access_token: accessToken
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received response:', data);
            createButton.textContent = 'Create Music Journey';
            createButton.disabled = false;

            const resultElement = document.getElementById('playlist-result');
            resultElement.classList.remove('hidden');

            // Clear previous results
            resultElement.innerHTML = '';

            const linkElement = document.createElement('div');
            linkElement.id = 'playlist-link';
            resultElement.appendChild(linkElement);

            // Check for error in the response
            if (data.error) {
                console.error('Error in response:', data.error);
                linkElement.innerHTML = `<h3 class="error">Error: ${data.error}</h3>`;
                return;
            }

            // Check if name exists
            if (data.name) {
                linkElement.innerHTML = `<h3>${data.name}</h3>`;
            } else {
                linkElement.innerHTML = `<h3>Your Recommendations</h3>`;
            }

            // Display warning if any
            if (data.warning) {
                const warningElement = document.createElement('div');
                warningElement.className = 'warning';
                warningElement.textContent = data.warning;
                linkElement.appendChild(warningElement);
            }

            // Display recommended tracks as a journey
            if (data.tracks && data.tracks.length > 0) {
                const tracksList = document.createElement('div');
                tracksList.className = 'playlist-tracks';
                tracksList.innerHTML = '<h4>Your Music Journey:</h4>';

                // Define the moods we're looking for
                const moods = ['high_energy', 'vibey', 'melancholic', 'sad', 'upbeat'];
                const moodNames = {
                    'high_energy': 'High Energy',
                    'vibey': 'Vibey & Ambient',
                    'melancholic': 'Melancholic & Nostalgic',
                    'sad': 'Emotional & Sad',
                    'upbeat': 'Upbeat & Bouncy'
                };

                // Group tracks by mood based on their position in the array
                // This assumes the tracks are returned in the order of the moods
                const tracksPerMood = Math.ceil(data.tracks.length / moods.length);

                // Create a section for each mood
                let trackIndex = 0;
                moods.forEach((mood, moodIndex) => {
                    // Get tracks for this mood
                    const moodTracks = data.tracks.slice(
                        moodIndex * tracksPerMood,
                        Math.min((moodIndex + 1) * tracksPerMood, data.tracks.length)
                    );

                    if (moodTracks.length > 0) {
                        // Create a section for this mood
                        const moodSection = document.createElement('div');
                        moodSection.className = 'mood-section';
                        moodSection.innerHTML = `<h5>${moodNames[mood]}</h5><ul>`;

                        // Add tracks to this mood section
                        moodTracks.forEach(track => {
                            const artists = track.artists.map(artist => artist.name).join(', ');
                            moodSection.innerHTML += `<li>${track.name} - ${artists}</li>`;
                        });

                        moodSection.innerHTML += '</ul>';
                        tracksList.appendChild(moodSection);
                    }
                });

                resultElement.appendChild(tracksList);
            } else {
                const noTracksElement = document.createElement('p');
                noTracksElement.textContent = 'No tracks found based on your prompt. Try a different description.';
                resultElement.appendChild(noTracksElement);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            createButton.textContent = 'Create Music Journey';
            createButton.disabled = false;
            alert(`Failed to create music journey: ${error.message}`);
        });
    }
});