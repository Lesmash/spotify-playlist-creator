# Deployment Guide for Spotify Playlist Creator

This guide provides step-by-step instructions for deploying the Spotify Playlist Creator application to GitHub Pages (frontend) and Render (backend).

## Prerequisites

1. A GitHub account
2. A Spotify Developer account
3. A Render account (free tier is sufficient)

## Step 1: Fork or Clone the Repository

1. Fork this repository to your GitHub account or clone it and push to a new repository.

## Step 2: Set Up Spotify Developer Account

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app name and description
5. Click "Create"
6. Note your Client ID and Client Secret
7. Click "Edit Settings"
8. Add the following Redirect URIs:
   - `http://localhost:5000/callback` (for local development)
   - `https://your-backend-url.onrender.com/callback` (for production, you'll update this after deploying the backend)
9. Click "Save"

## Step 3: Deploy the Backend to Render

1. Go to [Render](https://render.com/) and sign up or log in
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Fill in the following details:
   - Name: `spotify-playlist-creator-backend` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
5. Add the following environment variables:
   - `SPOTIFY_CLIENT_ID`: Your Spotify Client ID
   - `SPOTIFY_CLIENT_SECRET`: Your Spotify Client Secret
   - `REDIRECT_URI`: `https://your-backend-url.onrender.com/callback` (replace with your actual Render URL once deployed)
6. Click "Create Web Service"
7. Wait for the deployment to complete (this may take a few minutes)
8. Note the URL of your deployed backend (e.g., `https://spotify-playlist-creator-backend.onrender.com`)

## Step 4: Update the Spotify Redirect URI

1. Go back to your Spotify Developer Dashboard
2. Click on your app
3. Click "Edit Settings"
4. Update the Redirect URI with your actual Render backend URL:
   - `https://your-backend-url.onrender.com/callback`
5. Click "Save"

## Step 5: Update the Code with Your URLs

1. In `backend/app.py`, update the GitHub Pages URL:
   ```python
   GITHUB_PAGES_URL = "https://YOUR_GITHUB_USERNAME.github.io"
   ```
   Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

2. In `frontend/script.js`, update the backend URL:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.onrender.com';
   ```
   Replace with your actual Render backend URL.

3. Commit and push these changes to your GitHub repository.

## Step 6: Deploy the Frontend to GitHub Pages

1. Go to your GitHub repository
2. Click on "Settings"
3. Scroll down to the "GitHub Pages" section
4. Under "Source", select the branch you want to deploy (usually `main` or `master`)
5. Click "Save"
6. Wait for the deployment to complete
7. Your site will be published at `https://your-github-username.github.io/spotify-playlist-creator/`

## Step 7: Test the Application

1. Go to your GitHub Pages URL: `https://your-github-username.github.io/spotify-playlist-creator/`
2. Click "Connect with Spotify"
3. Log in with your Spotify account and authorize the application
4. You should be redirected back to your application with your Spotify data displayed
5. Try creating a playlist!

## Troubleshooting

### Backend Deployment Issues

- **ModuleNotFoundError**: Make sure your `wsgi.py` file is in the root directory and correctly imports the app.
- **Environment Variables**: Double-check that all environment variables are set correctly in Render.
- **CORS Errors**: Ensure the CORS configuration in `app.py` includes your GitHub Pages URL.

### Frontend Deployment Issues

- **404 Errors**: Make sure your repository is correctly set up for GitHub Pages.
- **API Connection Issues**: Check that the `API_BASE_URL` in `script.js` points to your Render backend URL.
- **Redirect Issues**: Verify that the Spotify redirect URI matches your Render backend URL.

## Local Development

To run the application locally:

1. Create a `.env` file in the `backend` directory with your Spotify credentials:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://localhost:5000/callback
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the backend:
   ```
   python backend/app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`
