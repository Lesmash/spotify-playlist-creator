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

    if (accessToken) {
        // Remove the access token from URL for security
        window.history.replaceState({}, document.title, window.location.pathname);
        showApp();
        loadUserProfile();
        loadTopArtists();
        loadTopTracks();
    } else {
        showLogin();
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
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('app-section').classList.remove('hidden');
        document.getElementById('user-profile').classList.remove('hidden');
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
            alert('Please enter a description for your playlist');
            return;
        }

        const createButton = document.getElementById('create-playlist-button');
        createButton.textContent = 'Creating...';
        createButton.disabled = true;

        fetch(`${API_BASE_URL}/create-playlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                access_token: accessToken,
                prompt: prompt
            })
        })
        .then(response => response.json())
        .then(data => {
            createButton.textContent = 'Create Playlist';
            createButton.disabled = false;

            const resultElement = document.getElementById('playlist-result');
            resultElement.classList.remove('hidden');

            const linkElement = document.getElementById('playlist-link');
            linkElement.innerHTML = `<a href="${data.external_url}" target="_blank">${data.name}</a>`;

            // Display tracks that were added to the playlist
            if (data.tracks && data.tracks.length > 0) {
                const tracksList = document.createElement('div');
                tracksList.className = 'playlist-tracks';
                tracksList.innerHTML = '<h4>Tracks added:</h4><ul>';

                data.tracks.forEach(track => {
                    tracksList.innerHTML += `<li>${track.name} - ${track.artists[0].name}</li>`;
                });

                tracksList.innerHTML += '</ul>';
                resultElement.appendChild(tracksList);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            createButton.textContent = 'Create Playlist';
            createButton.disabled = false;
            alert('Failed to create playlist. Please try again.');
        });
    }
});