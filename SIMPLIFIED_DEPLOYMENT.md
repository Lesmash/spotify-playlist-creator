# Simplified Deployment Guide

This guide provides simplified instructions for deploying the Spotify Playlist Creator to GitHub Pages and Render.

## Deploying to Render

1. Create an account on [Render](https://render.com/)
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Fill in the following details:
   - Name: `spotify-playlist-creator` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add the following environment variables:
   - `SPOTIFY_CLIENT_ID`: Your Spotify Client ID
   - `SPOTIFY_CLIENT_SECRET`: Your Spotify Client Secret
   - `REDIRECT_URI`: `https://your-render-url.onrender.com/callback` (replace with your actual Render URL once deployed)
6. Click "Create Web Service"
7. Wait for the deployment to complete
8. Note the URL of your deployed service (e.g., `https://spotify-playlist-creator.onrender.com`)

## Setting Up Spotify Developer Account

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app name and description
5. Click "Create"
6. Note your Client ID and Client Secret
7. Click "Edit Settings"
8. Add the following Redirect URI:
   - `https://your-render-url.onrender.com/callback` (replace with your actual Render URL)
9. Click "Save"

## Updating the Code

1. In `app.py`, update the GitHub Pages URL:
   ```python
   GITHUB_PAGES_URL = "https://YOUR_GITHUB_USERNAME.github.io"
   ```
   Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

2. Commit and push these changes to your GitHub repository.

## Deploying to GitHub Pages

1. Go to your GitHub repository
2. Click on "Settings"
3. Scroll down to the "GitHub Pages" section
4. Under "Source", select the branch you want to deploy (usually `main` or `master`)
5. Click "Save"
6. Wait for the deployment to complete
7. Your site will be published at `https://your-github-username.github.io/spotify-playlist-creator/`

## Testing the Application

1. Go to your GitHub Pages URL: `https://your-github-username.github.io/spotify-playlist-creator/`
2. Click "Connect with Spotify"
3. Log in with your Spotify account and authorize the application
4. You should be redirected back to your application with your Spotify data displayed
5. Try creating a playlist!
