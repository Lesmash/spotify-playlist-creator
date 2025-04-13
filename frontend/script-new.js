document.addEventListener('DOMContentLoaded', () => {
    // This will work with both local development and production
    // For production, replace with your actual Render URL
    const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? '' // Use relative URL for local development
        : 'https://spotify-playlist-creator-1a7x.onrender.com'; // Your actual Render URL
    
    let accessToken = null;
    let journeyHistory = [];

    // Check if we have an access token in the URL (after redirect)
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    accessToken = hashParams.get('access_token');

    // Initialize theme
    initTheme();
    
    // Initialize template buttons
    initTemplateButtons();

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
        
        // Load journey history from localStorage
        loadJourneyHistory();
    } else {
        // Show login section but keep app section visible for demo
        document.getElementById('login-section').classList.remove('hidden');
    }

    // Event Listeners
    document.getElementById('login-button').addEventListener('click', login);
    document.getElementById('create-playlist-button').addEventListener('click', createPlaylist);
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

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

        // Show loading indicator
        document.getElementById('loading-indicator').classList.remove('hidden');
        // Hide any previous results
        document.getElementById('playlist-result').classList.add('hidden');

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
            // Hide loading indicator
            document.getElementById('loading-indicator').classList.add('hidden');
            
            // Reset button
            createButton.textContent = 'Create Music Journey';
            createButton.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 8px; vertical-align: middle;">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM17 13H13V17H11V13H7V11H11V7H13V11H17V13Z" fill="white"/>
                </svg>
                Create Music Journey
            `;
            createButton.disabled = false;
            
            // Show results
            const resultElement = document.getElementById('playlist-result');
            resultElement.classList.remove('hidden');
            resultElement.innerHTML = '';
            
            // Add to history if we have a valid result
            if (data.tracks && data.tracks.length > 0) {
                addToHistory(prompt, data);
            }

            // Display Spotify playlist link if available
            if (data.playlist_url) {
                const playlistLinkElement = document.createElement('div');
                playlistLinkElement.id = 'playlist-link';
                playlistLinkElement.innerHTML = `
                    <a href="${data.playlist_url}" target="_blank">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM16.5 16.5C16.27 16.73 15.9 16.73 15.67 16.5C14.55 15.39 13.04 14.8 11.42 14.8C9.8 14.8 8.29 15.39 7.17 16.5C6.94 16.73 6.57 16.73 6.34 16.5C6.11 16.27 6.11 15.9 6.34 15.67C7.74 14.27 9.54 13.5 11.42 13.5C13.3 13.5 15.1 14.27 16.5 15.67C16.73 15.9 16.73 16.27 16.5 16.5ZM17.79 13.21C17.56 13.44 17.19 13.44 16.96 13.21C15.54 11.79 13.55 11 11.42 11C9.29 11 7.3 11.79 5.88 13.21C5.65 13.44 5.28 13.44 5.05 13.21C4.82 12.98 4.82 12.61 5.05 12.38C6.75 10.68 9.02 9.75 11.42 9.75C13.82 9.75 16.09 10.68 17.79 12.38C18.02 12.61 18.02 12.98 17.79 13.21Z" fill="#1DB954"/>
                        </svg>
                        Open Playlist in Spotify
                    </a>
                `;
                resultElement.appendChild(playlistLinkElement);
            }

            // Display recommended tracks as a journey
            if (data.tracks && data.tracks.length > 0) {
                const tracksList = document.createElement('div');
                tracksList.className = 'playlist-tracks';
                tracksList.innerHTML = '<h4>Your AI-Generated Music Journey:</h4>';

                // Define the moods we're looking for
                const moodNames = {
                    'high_energy': 'High Energy',
                    'vibey': 'Vibey & Ambient',
                    'melancholic': 'Melancholic & Nostalgic',
                    'sad': 'Emotional & Sad',
                    'upbeat': 'Upbeat & Bouncy',
                    'custom': 'Your Requested Tracks',
                    // Add fallbacks for other possible mood values
                    'energetic': 'Energetic',
                    'chill': 'Chill & Relaxed',
                    'nostalgic': 'Nostalgic',
                    'emotional': 'Emotional',
                    'happy': 'Happy & Upbeat'
                };

                // Group tracks by their mood property
                const tracksByMood = {};

                // First, organize tracks by mood
                data.tracks.forEach(track => {
                    const mood = track.mood ? track.mood.toLowerCase() : 'other';
                    if (!tracksByMood[mood]) {
                        tracksByMood[mood] = [];
                    }
                    tracksByMood[mood].push(track);
                });

                // Create a section for each mood that has tracks
                Object.keys(tracksByMood).forEach(mood => {
                    const moodTracks = tracksByMood[mood];
                    if (moodTracks.length > 0) {
                        const moodSection = document.createElement('div');
                        moodSection.className = 'mood-section';
                        
                        // Get a nice display name for the mood
                        const moodDisplayName = moodNames[mood] || mood.charAt(0).toUpperCase() + mood.slice(1);
                        
                        moodSection.innerHTML = `<h5>${moodDisplayName}</h5><ul>`;
                        
                        moodTracks.forEach(track => {
                            const artistNames = track.artists.map(artist => artist.name).join(', ');
                            const albumName = track.album ? track.album.name : '';
                            
                            moodSection.innerHTML += `
                                <li>
                                    <div class="track-info">${track.name} - ${artistNames}</div>
                                    <div class="album-name">${albumName}</div>
                                    ${track.reason ? `<div class="track-reason">${track.reason}</div>` : ''}
                                </li>
                            `;
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
            createButton.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 8px; vertical-align: middle;">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM17 13H13V17H11V13H7V11H11V7H13V11H17V13Z" fill="white"/>
                </svg>
                Create Music Journey
            `;
            createButton.disabled = false;

            // Hide loading indicator
            document.getElementById('loading-indicator').classList.add('hidden');

            alert(`Failed to create music journey: ${error.message}`);
        });
    }
    
    function initTheme() {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
            updateThemeIcon(true);
        }
    }
    
    function toggleTheme() {
        const isLightTheme = document.body.classList.toggle('light-theme');
        updateThemeIcon(isLightTheme);
        
        // Save theme preference
        localStorage.setItem('theme', isLightTheme ? 'light' : 'dark');
    }
    
    function updateThemeIcon(isLightTheme) {
        const themeIcon = document.getElementById('theme-icon');
        if (isLightTheme) {
            themeIcon.innerHTML = `
                <path d="M12 7C9.24 7 7 9.24 7 12C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12C17 9.24 14.76 7 12 7ZM2 13H4C4.55 13 5 12.55 5 12C5 11.45 4.55 11 4 11H2C1.45 11 1 11.45 1 12C1 12.55 1.45 13 2 13ZM20 13H22C22.55 13 23 12.55 23 12C23 11.45 22.55 11 22 11H20C19.45 11 19 11.45 19 12C19 12.55 19.45 13 20 13ZM11 2V4C11 4.55 11.45 5 12 5C12.55 5 13 4.55 13 4V2C13 1.45 12.55 1 12 1C11.45 1 11 1.45 11 2ZM11 20V22C11 22.55 11.45 23 12 23C12.55 23 13 22.55 13 22V20C13 19.45 12.55 19 12 19C11.45 19 11 19.45 11 20ZM5.99 4.58C5.6 4.19 4.96 4.19 4.58 4.58C4.19 4.97 4.19 5.61 4.58 5.99L5.64 7.05C6.03 7.44 6.67 7.44 7.05 7.05C7.44 6.66 7.44 6.02 7.05 5.64L5.99 4.58ZM18.36 16.95C17.97 16.56 17.33 16.56 16.95 16.95C16.56 17.34 16.56 17.98 16.95 18.36L18.01 19.42C18.4 19.81 19.04 19.81 19.42 19.42C19.81 19.03 19.81 18.39 19.42 18.01L18.36 16.95ZM19.42 5.99C19.81 5.6 19.81 4.96 19.42 4.58C19.03 4.19 18.39 4.19 18.01 4.58L16.95 5.64C16.56 6.03 16.56 6.67 16.95 7.05C17.34 7.44 17.98 7.44 18.36 7.05L19.42 5.99ZM7.05 18.36C7.44 17.97 7.44 17.33 7.05 16.95C6.66 16.56 6.02 16.56 5.64 16.95L4.58 18.01C4.19 18.4 4.19 19.04 4.58 19.42C4.97 19.81 5.61 19.81 5.99 19.42L7.05 18.36Z" fill="#333"/>
            `;
        } else {
            themeIcon.innerHTML = `
                <path d="M20 8.69V4H15.31L12 0.69L8.69 4H4V8.69L0.69 12L4 15.31V20H8.69L12 23.31L15.31 20H20V15.31L23.31 12L20 8.69ZM12 18C8.69 18 6 15.31 6 12C6 8.69 8.69 6 12 6C15.31 6 18 8.69 18 12C18 15.31 15.31 18 12 18ZM12 8C9.79 8 8 9.79 8 12C8 14.21 9.79 16 12 16C14.21 16 16 14.21 16 12C16 9.79 14.21 8 12 8Z" fill="white"/>
            `;
        }
    }
    
    function initTemplateButtons() {
        const templateButtons = document.querySelectorAll('.template-button');
        templateButtons.forEach(button => {
            button.addEventListener('click', () => {
                const template = button.getAttribute('data-template');
                document.getElementById('playlist-prompt').value = template;
            });
        });
    }
    
    function addToHistory(prompt, data) {
        // Only store if we have access token (logged in)
        if (!accessToken) return;
        
        const historyItem = {
            id: Date.now(),
            prompt: prompt,
            timestamp: new Date().toISOString(),
            trackCount: data.tracks ? data.tracks.length : 0
        };
        
        // Add to beginning of array
        journeyHistory.unshift(historyItem);
        
        // Limit history to 10 items
        if (journeyHistory.length > 10) {
            journeyHistory = journeyHistory.slice(0, 10);
        }
        
        // Save to localStorage
        localStorage.setItem('journeyHistory', JSON.stringify(journeyHistory));
        
        // Update history display
        updateHistoryDisplay();
    }
    
    function loadJourneyHistory() {
        const savedHistory = localStorage.getItem('journeyHistory');
        if (savedHistory) {
            journeyHistory = JSON.parse(savedHistory);
            updateHistoryDisplay();
        }
    }
    
    function updateHistoryDisplay() {
        const historySection = document.getElementById('history-section');
        const historyList = document.getElementById('history-list');
        
        // Show history section if we have items
        if (journeyHistory.length > 0) {
            historySection.classList.remove('hidden');
            
            // Clear current list
            historyList.innerHTML = '';
            
            // Add history items
            journeyHistory.forEach(item => {
                const historyItem = document.createElement('li');
                historyItem.className = 'history-item';
                
                // Format date
                const date = new Date(item.timestamp);
                const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                
                historyItem.innerHTML = `
                    <div class="history-prompt">
                        <strong>${item.prompt.substring(0, 50)}${item.prompt.length > 50 ? '...' : ''}</strong>
                        <div class="history-date">${formattedDate} (${item.trackCount} tracks)</div>
                    </div>
                    <div class="history-actions">
                        <button class="reuse-prompt" data-prompt="${encodeURIComponent(item.prompt)}">Reuse</button>
                        <button class="delete-history" data-id="${item.id}">Delete</button>
                    </div>
                `;
                
                historyList.appendChild(historyItem);
            });
            
            // Add event listeners
            document.querySelectorAll('.reuse-prompt').forEach(button => {
                button.addEventListener('click', () => {
                    const prompt = decodeURIComponent(button.getAttribute('data-prompt'));
                    document.getElementById('playlist-prompt').value = prompt;
                    // Scroll to prompt
                    document.getElementById('playlist-prompt').scrollIntoView({behavior: 'smooth'});
                });
            });
            
            document.querySelectorAll('.delete-history').forEach(button => {
                button.addEventListener('click', () => {
                    const id = parseInt(button.getAttribute('data-id'));
                    deleteHistoryItem(id);
                });
            });
        } else {
            historySection.classList.add('hidden');
        }
    }
    
    function deleteHistoryItem(id) {
        journeyHistory = journeyHistory.filter(item => item.id !== id);
        localStorage.setItem('journeyHistory', JSON.stringify(journeyHistory));
        updateHistoryDisplay();
    }
});
