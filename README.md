# Spotify Playlist Creator

A web application that uses the Spotify API to create personalized playlists based on your music taste.

## Deployment Instructions

### Frontend (GitHub Pages)

1. Fork this repository
2. In your forked repository, go to Settings > Pages
3. Set the source to the main branch
4. Your site will be published at `https://<your-github-username>.github.io/spotify-playlist-creator/`

### Backend (Render, Heroku, or similar)

1. Create an account on [Render](https://render.com/) or [Heroku](https://www.heroku.com/)
2. Create a new Web Service and connect it to your GitHub repository
3. Set the following environment variables:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=https://your-backend-url.onrender.com/callback
   ```
4. Deploy the application

### Spotify Developer Setup

1. Create a Spotify Developer account and register a new application at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Add the following Redirect URIs in your Spotify app settings:
   - `https://your-backend-url.onrender.com/callback` (for production)
   - `http://localhost:5000/callback` (for local development)
3. Update the frontend code in `frontend/script.js` to point to your backend URL
4. Update the backend code in `backend/app.py` to include your GitHub Pages URL in the CORS configuration and redirect URL

## Local Development Setup

1. Clone the repository
2. Create a `.env` file in the `backend` directory with the following content:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://localhost:5000/callback
   ```
3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the backend:
   ```
   python backend/app.py
   ```
5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Features

- Connect with your Spotify account
- View your top artists and tracks
- Create personalized playlists based on your music taste
- Open created playlists directly in Spotify

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- API: Spotify Web API
- Hosting: GitHub Pages (frontend) and Render/Heroku (backend)
