import os
from flask import Flask, session, redirect, request, url_for, render_template_string
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
# Use a secure random secret key for session management.
app.secret_key = "YOUR_RANDOM_SECRET_KEY"  # Change this!

# Define the Spotify API scope we need.
# (We need permissions to read the player’s state and to control playback.)
SCOPE = "user-read-playback-state user-modify-playback-state"

# In-memory store for timestamps (for demonstration purposes).
# In production you might want to use a database.
timestamp_store = []  # Each item will be a dict: { "track_uri", "timestamp", "description" }

# ------------------------------
# Helper: Render the main page
# ------------------------------
@app.route("/")
def index():
    if "token_info" not in session:
        return redirect(url_for("login"))
    
    # Main page shows a form to add a new timestamp and a list of stored timestamps.
    html = """
    <h1>Spotify Timestamp Manager</h1>
    <p><a href="{{ url_for('logout') }}">Logout</a></p>
    
    <h2>Add a New Timestamp</h2>
    <form action="{{ url_for('add_timestamp') }}" method="post">
        <label>Spotify Track URI or URL: 
            <input type="text" name="track_uri" required>
        </label><br><br>
        <label>Timestamp (in seconds): 
            <input type="number" name="timestamp" required>
        </label><br><br>
        <label>Description: 
            <input type="text" name="description" placeholder="E.g., My favorite chorus">
        </label><br><br>
        <input type="submit" value="Add Timestamp">
    </form>
    
    <h2>Saved Timestamps</h2>
    <ul>
    {% for item in timestamp_store %}
      <li>
         <strong>{{ item.description }}</strong> — 
         Track: {{ item.track_uri }} — 
         Timestamp: {{ item.timestamp }} sec 
         (<a href="{{ url_for('play_timestamp', index=loop.index0) }}">Play from here</a>)
      </li>
    {% else %}
      <li>No timestamps saved yet.</li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, timestamp_store=timestamp_store)

# ------------------------------
# Spotify Login Routes
# ------------------------------
@app.route("/login")
def login():
    sp_oauth = SpotifyOAuth(scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    sp_oauth = SpotifyOAuth(scope=SCOPE)
    session.clear()  # Clear any previous session
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ------------------------------
# Add a Timestamp Route
# ------------------------------
@app.route("/add_timestamp", methods=["POST"])
def add_timestamp():
    if "token_info" not in session:
        return redirect(url_for("login"))
    
    track_uri = request.form.get("track_uri")
    timestamp = request.form.get("timestamp")
    description = request.form.get("description") or "No description"
    
    # Convert the timestamp to an integer (seconds)
    try:
        timestamp = int(timestamp)
    except ValueError:
        return "Invalid timestamp", 400

    # Normalize track_uri: if a Spotify URL is provided, convert it to a URI.
    if "open.spotify.com/track/" in track_uri:
        # e.g., https://open.spotify.com/track/TRACKID?si=...
        parts = track_uri.split("/")
        track_id = parts[-1].split("?")[0]
        track_uri = "spotify:track:" + track_id

    # Save the timestamp record.
    timestamp_store.append({
        "track_uri": track_uri,
        "timestamp": timestamp,
        "description": description
    })
    return redirect(url_for("index"))

# ------------------------------
# Play a Timestamp Route
# ------------------------------
@app.route("/play/<int:index>")
def play_timestamp(index):
    if "token_info" not in session:
        return redirect(url_for("login"))
    if index < 0 or index >= len(timestamp_store):
        return "Invalid index", 400

    sp = spotipy.Spotify(auth=session["token_info"]["access_token"])
    item = timestamp_store[index]
    track_uri = item["track_uri"]
    timestamp_sec = item["timestamp"]
    timestamp_ms = timestamp_sec * 1000  # Spotify expects milliseconds

    # Start playback for the track from the desired position.
    try:
        sp.start_playback(uris=[track_uri], position_ms=timestamp_ms)
    except spotipy.exceptions.SpotifyException as e:
        return f"Error starting playback: {e}", 400

    return redirect(url_for("index"))

# ------------------------------
# Run the Flask App
# ------------------------------
if __name__ == "__main__":
    # Run on localhost:5000
    app.run(debug=True)
