# Spotify Playlist Creator

A web application that uses the Spotify API to create personalized playlists based on your music taste.

## Simplified Deployment Instructions

### Important Note

This application uses specific versions of Flask and Werkzeug to avoid compatibility issues. The requirements.txt file includes these specific versions:

```
flask==2.0.1
werkzeug==2.0.1
```

### Deploy to Render

1. Create an account on [Render](https://render.com/)
2. Create a new Web Service and connect it to your GitHub repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
4. Add the following environment variables:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=https://your-render-url.onrender.com/callback
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   ```
5. Deploy the application

### Update the Code

1. In `app.py`, update the GitHub Pages URL:
   ```python
   GITHUB_PAGES_URL = "https://YOUR_GITHUB_USERNAME.github.io"
   ```

2. In `frontend/script.js`, update the backend URL:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
       ? '' // Use relative URL for local development
       : 'https://your-render-url.onrender.com'; // Replace with your Render URL
   ```

### Spotify Developer Setup

1. Create a Spotify Developer account and register an application at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Add the following Redirect URI in your Spotify app settings:
   - `https://your-render-url.onrender.com/callback`

## Local Development

1. Create a `.env` file in the root directory with the following content:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://localhost:5000/callback
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   ```

   You can get a free Hugging Face API key by creating an account at [Hugging Face](https://huggingface.co/) and generating a token in your account settings.

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Features

- Connect with your Spotify account
- View your top artists and tracks
- Create personalized playlists based on your music taste
- AI-powered music journey recommendations
- Detailed explanations for why each song was selected
- Open created playlists directly in Spotify

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- APIs: Spotify Web API, Hugging Face Inference API
- AI: Mistral-7B-Instruct for music recommendations
- Hosting: Render
