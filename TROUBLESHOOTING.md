# Troubleshooting Guide

This guide provides solutions to common issues you might encounter when deploying the Spotify Playlist Creator.

## Deployment Issues on Render

### ImportError: cannot import name 'url_quote' from 'werkzeug.urls'

**Problem**: This error occurs when Flask and Werkzeug versions are incompatible.

**Solution**:
1. Make sure your requirements.txt includes specific versions of both Flask and Werkzeug:
   ```
   flask==2.0.1
   werkzeug==2.0.1
   ```
2. Redeploy your application on Render.

### ModuleNotFoundError: No module named 'app'

**Problem**: Gunicorn can't find the app module.

**Solution**:
1. Make sure you're using the correct start command in Render:
   ```
   gunicorn wsgi:app
   ```
2. Verify that both app.py and wsgi.py are in the root directory of your repository.
3. Check that wsgi.py correctly imports the app:
   ```python
   from app import app
   ```

### Other Dependency Issues

**Problem**: You might encounter other dependency-related errors.

**Solution**:
1. Try specifying a Python version in a runtime.txt file:
   ```
   python-3.9.0
   ```
2. Make sure all dependencies are listed in requirements.txt with specific versions.

## Spotify API Issues

### INVALID_CLIENT Error

**Problem**: This occurs when your Spotify API credentials are incorrect or not properly configured.

**Solution**:
1. Double-check your Client ID and Client Secret in the Render environment variables.
2. Verify that the Redirect URI in your Spotify Developer Dashboard matches exactly what you've set in your Render environment variables.
3. Make sure your application is properly registered in the Spotify Developer Dashboard.

### Redirect URI Mismatch

**Problem**: Spotify returns an error about the redirect URI not matching.

**Solution**:
1. In your Spotify Developer Dashboard, add the exact redirect URI that your application uses:
   ```
   https://your-render-url.onrender.com/callback
   ```
2. Make sure the REDIRECT_URI environment variable in Render matches this exactly.

## Frontend Issues

### API Connection Issues

**Problem**: The frontend can't connect to the backend API.

**Solution**:
1. Make sure you've updated the API_BASE_URL in frontend/script.js with your actual Render URL:
   ```javascript
   const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
       ? '' // Use relative URL for local development
       : 'https://your-render-url.onrender.com'; // Replace with your Render URL
   ```
2. Check that CORS is properly configured in app.py to allow requests from your GitHub Pages URL.

### GitHub Pages Not Updating

**Problem**: Changes to your frontend code aren't reflected on GitHub Pages.

**Solution**:
1. Make sure you've pushed your changes to the correct branch (usually main or master).
2. Check the GitHub Pages settings in your repository to ensure it's publishing from the correct branch.
3. It may take a few minutes for changes to propagate.

## Local Development Issues

### Environment Variables Not Loading

**Problem**: The application can't find your Spotify credentials.

**Solution**:
1. Make sure you have a .env file in the root directory with the following content:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://localhost:5000/callback
   ```
2. Verify that python-dotenv is installed:
   ```
   pip install python-dotenv
   ```

### Flask Development Server Issues

**Problem**: The Flask development server won't start.

**Solution**:
1. Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```
2. Check for error messages in the console.
3. Try running with debug mode:
   ```
   python app.py
   ```
