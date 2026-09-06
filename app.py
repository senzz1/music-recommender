from flask import Flask, request, session, redirect, url_for
import requests
from dotenv import load_dotenv
import os
import random
import urllib.parse

load_dotenv()
api_key = os.getenv("LASTFM_API_KEY")
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

STYLE = """
<style>
    :root {
        --theme-accent: #fa243c;
        --bg-dark: #000000;
        --card-bg: #1c1c1e;
        --card-bg-2: #232325;
        --text-primary: #ffffff;
        --text-secondary: #a1a1a6;
    }

    * { -webkit-tap-highlight-color: transparent; }

    body { 
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
        background: var(--bg-dark); color: var(--text-primary); 
        margin: 0; padding: 0; 
        display: flex; flex-direction: column; min-height: 100vh;
    }
    
    .container { 
        max-width: 1180px; width: 100%; margin: 0 auto; 
        padding: 56px 32px 130px 32px; box-sizing: border-box;
        display: flex; flex-direction: column; align-items: center; flex: 1;
    }

    .page-center {
        flex: 1; width: 100%; max-width: 1040px;
        display: flex; flex-direction: column; justify-content: center;
    }

    .top-bar {
        width: 100%; margin-bottom: 32px;
    }
    .top-bar .top-title {
        font-size: 2.4em; font-weight: 800; letter-spacing: -0.6px; display: block;
    }
    .top-bar .accent-rule {
        width: 56px; height: 4px; border-radius: 4px; margin-top: 14px;
        background: linear-gradient(90deg, var(--theme-accent), #ff8a97);
    }
    
    h1 { color: var(--text-primary); font-weight: 800; font-size: 2.2em; margin-bottom: 8px; text-align: left; letter-spacing: -0.5px; }
    h2 { font-size: 1.4em; font-weight: 700; margin-top: 30px; margin-bottom: 16px; border-bottom: 1px solid #2c2c2e; padding-bottom: 8px; letter-spacing: -0.3px; }
    a { color: var(--theme-accent); text-decoration: none; }
    
    .tagline { color: var(--text-secondary); font-size: 1.1em; margin-top: 0; margin-bottom: 28px; line-height: 1.45; }

    .search-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        align-items: stretch;
        gap: 36px;
        width: 100%;
    }

    .form-card, .rec-sidebar {
        background: linear-gradient(180deg, var(--card-bg-2), var(--card-bg));
        border-radius: 24px;
        padding: 44px 40px;
        border: 1px solid #2c2c2e;
        box-shadow: 0 16px 50px rgba(0,0,0,0.55);
        width: 100%;
        min-height: 420px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .rec-sidebar h3 { color: #fff; margin-top: 0; font-size: 1.3em; margin-bottom: 22px; font-weight: 700; letter-spacing: -0.3px; }
    
    .rec-item {
        display: flex;
        align-items: center;
        gap: 16px;
        background: #2c2c2e;
        padding: 12px 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        text-decoration: none;
        color: var(--text-primary);
        transition: background 0.2s, transform 0.1s;
        border: none;
        width: 100%;
        text-align: left;
        cursor: pointer;
        font-family: inherit;
        box-sizing: border-box;
    }
    .rec-item:hover { background: #3a3a3c; transform: translateX(3px); }
    .rec-item:last-child { margin-bottom: 0; }
    
    .rec-item img {
        width: 56px;
        height: 56px;
        border-radius: 10px;
        object-fit: cover;
        background: #000;
        flex-shrink: 0;
    }
    .rec-item.artist-rec img { border-radius: 50%; } 
    
    .rec-info { display: flex; flex-direction: column; overflow: hidden; }
    .rec-title { font-weight: 600; font-size: 1em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff; }
    .rec-sub { color: var(--text-secondary); font-size: 0.88em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }

    form.search-form { display: flex; flex-direction: column; gap: 16px; width: 100%; margin: 0; }
    input[type=text], select { 
        padding: 15px 16px; border-radius: 12px; border: none; background: #2c2c2e; 
        color: var(--text-primary); font-size: 1.05em; outline: none; transition: background 0.2s; width: 100%; box-sizing: border-box;
        -webkit-appearance: none; appearance: none;
    }
    input[type=text]:focus, select:focus { background: #3a3a3c; }
    input::placeholder { color: #8e8e93; }
    
    label { display: flex; align-items: center; gap: 10px; color: var(--text-secondary); font-size: 0.95em; cursor: pointer; margin-top: 2px; }
    input[type=checkbox] { width: 18px; height: 18px; accent-color: var(--theme-accent); cursor: pointer; }
    
    button[type=submit].main-btn { 
        background: linear-gradient(135deg, var(--theme-accent), #ff5a6e); border: none; padding: 16px; border-radius: 12px; 
        color: #fff; font-size: 1.05em; font-weight: 700; cursor: pointer; 
        transition: transform 0.1s, filter 0.2s; width: 100%; margin-top: 8px;
    }
    button[type=submit].main-btn:hover { filter: brightness(1.1); transform: scale(0.98); }

    .info-card {
        background: #1c1c1e; border-radius: 16px; padding: 24px; margin-top: 30px;
        border: 1px solid #2c2c2e; line-height: 1.5; color: var(--text-secondary); max-width: 860px; width: 100%; box-sizing: border-box;
    }
    .info-card h3 { color: var(--text-primary); margin-top: 0; font-size: 1.15em; }
    .info-card ul { padding-left: 20px; margin: 10px 0 0 0; }
    .info-card li { margin-bottom: 8px; }

    .results-grid {
        display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); 
        gap: 24px; width: 100%; max-width: 1040px; padding: 0; margin: 0 auto; list-style: none;
    }
    
    .result-card { display: flex; flex-direction: column; align-items: flex-start; }
    .result-card img { 
        width: 100%; aspect-ratio: 1 / 1; border-radius: 10px; object-fit: cover; 
        background: #2c2c2e; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }
    .result-card.artist-card img { border-radius: 50%; } 
    
    .result-card .title { font-weight: 600; font-size: 1em; color: var(--text-primary); width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px; }
    .result-card .subtitle { color: var(--text-secondary); font-size: 0.85em; width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    
    .save-btn { 
        margin-top: 10px; background: #2c2c2e; color: var(--theme-accent); 
        border-radius: 20px; padding: 6px 14px; font-size: 0.85em; width: auto; border: none; cursor: pointer;
        font-weight: 600;
    }
    .save-btn:hover { background: #3a3a3c; }
    
    .back-link { display: inline-flex; align-items: center; gap: 4px; margin-top: 30px; font-weight: 600; font-size: 1.1em; color: var(--theme-accent); }

    .nav-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 20px; width: 100%; max-width: 860px; }
    .nav-card { 
        background: #1c1c1e; padding: 24px 20px; border-radius: 16px; text-align: left;
        display: flex; flex-direction: column; text-decoration: none; transition: transform 0.2s;
        border: 1px solid #2c2c2e;
    }
    .nav-card:hover { transform: scale(0.98); background: #2c2c2e; }
    .nav-icon-title { display: flex; align-items: center; gap: 12px; font-size: 1.2em; font-weight: 700; color: #fff; margin-bottom: 8px; }
    .nav-icon-title svg { width: 24px; height: 24px; stroke: var(--theme-accent); fill: none; stroke-width: 2; }
    .nav-card .desc { font-size: 0.9em; color: var(--text-secondary); line-height: 1.4; }

    .bottom-bar { 
        position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(28, 28, 30, 0.85); 
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        display: flex; justify-content: space-around; padding: 12px 0 calc(12px + env(safe-area-inset-bottom)); 
        border-top: 1px solid #333; z-index: 1000;
    }
    .bottom-bar a { display: flex; flex-direction: column; align-items: center; color: var(--text-secondary); font-size: 0.75em; font-weight: 500; gap: 4px; }
    .bottom-bar a:hover, .bottom-bar a:active { color: var(--theme-accent); }
    .bottom-bar svg { width: 24px; height: 24px; fill: currentColor; }

    .spinner { display: none; width: 24px; height: 24px; border: 3px solid #333; border-top: 3px solid var(--theme-accent); border-radius: 50%; animation: spin 1s linear infinite; margin: 10px auto; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

    @media(max-width: 880px) {
        .search-layout { grid-template-columns: 1fr; }
        .form-card, .rec-sidebar { max-width: 480px; margin: 0 auto; width: 100%; }
    }
</style>
<script>
    function showLoading() {
        document.getElementById('submit-btn').style.display = 'none';
        document.getElementById('loading-spinner').style.display = 'block';
    }
</script>
"""

BOTTOM_BAR = """
<div class="bottom-bar">
    <a href="/home">
        <svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg> Home
    </a>
    <a href="/history">
        <svg viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/><path d="M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg> History
    </a>
    <a href="/favorites">
        <svg viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg> Favorites
    </a>
</div>
"""

def page(title, body):
    return f"<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>{title}</title>{STYLE}</head><body><div class='container'>{body}</div>{BOTTOM_BAR}</body></html>"

def top_bar(title):
    return f"<div class='top-bar'><span class='top-title'>{title}</span><div class='accent-rule'></div></div>"

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def get_image(entity, entity_name="?"):
    bad_hashes = ["2a96cbd8b46e442fc41c2b86b821562f", "818148bf682d429dc215c1705eb27b98"]
    images = entity.get('image', [])
    for img in reversed(images):
        url = img.get('#text', '')
        if url and not any(bad in url for bad in bad_hashes):
            return url
    initial = entity_name[0].upper() if entity_name else "?"
    encoded_initial = urllib.parse.quote(initial)
    return f"https://placehold.co/200x200/2c2c2e/ffffff?text={encoded_initial}"

def get_artist_image_from_deezer(artist_name):
    try:
        url = f"https://api.deezer.com/search/artist?q={urllib.parse.quote(artist_name)}"
        res = requests.get(url).json()
        if 'data' in res and len(res['data']) > 0:
            return res['data'][0]['picture_xl'] 
    except Exception:
        pass
    initial = artist_name[0].upper() if artist_name else "?"
    encoded_initial = urllib.parse.quote(initial)
    return f"https://placehold.co/200x200/2c2c2e/ffffff?text={encoded_initial}"

def get_album_image_for_search(album_name, artist_name):
    url = f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={api_key}&artist={urllib.parse.quote(artist_name)}&album={urllib.parse.quote(album_name)}&format=json"
    try:
        res = requests.get(url).json()
        album_info = res.get('album', {})
        if 'image' in album_info:
            img_url = get_image(album_info, album_name)
            if img_url:
                return img_url
    except Exception:
        pass
    initial = album_name[0].upper() if album_name else "?"
    return f"https://placehold.co/200x200/2c2c2e/ffffff?text={urllib.parse.quote(initial)}"

def get_album_image_for_track(track_name, artist_name):
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={api_key}&artist={urllib.parse.quote(artist_name)}&track={urllib.parse.quote(track_name)}&format=json"
    try:
        response = requests.get(url).json()
        track_info = response.get('track', {})
        if 'album' in track_info and 'image' in track_info['album']:
            return get_image(track_info['album'], track_name)
        if 'image' in track_info:
            return get_image(track_info, track_name)
    except Exception:
        pass
    initial = track_name[0].upper() if track_name else "?"
    return f"https://placehold.co/200x200/2c2c2e/ffffff?text={urllib.parse.quote(initial)}"

def get_artist_info(artist_data):
    if isinstance(artist_data, dict):
        return artist_data.get('name', 'Unknown'), artist_data.get('url', '#')
    return artist_data, f"https://www.last.fm/music/{artist_data}"

def fetch_trending_artists(count=3):
    try:
        page = random.randint(1, 15)
        url = f"http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key={api_key}&format=json&limit=50&page={page}"
        data = requests.get(url, timeout=5).json()
        artists = data.get('artists', {}).get('artist', [])
        names = [a['name'] for a in artists if a.get('name')]
        if not names:
            return []
        return random.sample(names, min(count, len(names)))
    except Exception:
        return []

def fetch_trending_songs(count=3):
    try:
        page = random.randint(1, 15)
        url = f"http://ws.audioscrobbler.com/2.0/?method=chart.gettoptracks&api_key={api_key}&format=json&limit=50&page={page}"
        data = requests.get(url, timeout=5).json()
        tracks = data.get('tracks', {}).get('track', [])
        pairs = []
        for t in tracks:
            name = t.get('name')
            artist = t.get('artist', {})
            artist_name = artist.get('name') if isinstance(artist, dict) else artist
            if name and artist_name:
                pairs.append((name, artist_name))
        if not pairs:
            return []
        return random.sample(pairs, min(count, len(pairs)))
    except Exception:
        return []

def fetch_trending_albums(count=3):
    genre_tags = ["rock", "hip hop", "pop", "electronic", "indie", "jazz", "metal", "rnb", "alternative", "classic rock"]
    try:
        tag = random.choice(genre_tags)
        page = random.randint(1, 5)
        url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettopalbums&tag={urllib.parse.quote(tag)}&api_key={api_key}&format=json&limit=50&page={page}"
        data = requests.get(url, timeout=5).json()
        albums = data.get('albums', {}).get('album', [])
        pairs = []
        for al in albums:
            name = al.get('name')
            artist = al.get('artist', {})
            artist_name = artist.get('name') if isinstance(artist, dict) else artist
            if name and artist_name:
                pairs.append((name, artist_name))
        if not pairs:
            return []
        return random.sample(pairs, min(count, len(pairs)))
    except Exception:
        return []

@app.route('/home')
def landing():
    body = """
        <div style="width: 100%; max-width: 860px;">
            <h1>Music Recommender</h1>
            <p class="tagline">Discover new artists, tracks, and albums based on what you already love.</p>
            
            <h2>Discover by Category</h2>
            <div class="nav-grid">
                <a href="/search-artist" class="nav-card">
                    <div class="nav-icon-title">
                        <svg viewBox="0 0 24 24"><path d="M12 2a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/><path d="M6 11v1a6 6 0 0 0 12 0v-1"/><path d="M12 18v4"/><path d="M9 22h6"/></svg>
                        Artists
                    </div>
                    <span class="desc">Find creators similar to your favorites.</span>
                </a>
                <a href="/search-song" class="nav-card">
                    <div class="nav-icon-title">
                        <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
                        Songs
                    </div>
                    <span class="desc">Build the perfect playlist with matching vibes.</span>
                </a>
                <a href="/search_album" class="nav-card">
                    <div class="nav-icon-title">
                        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/></svg>
                        Albums
                    </div>
                    <span class="desc">Dive into full projects with similar sounds.</span>
                </a>
            </div>

            <div class="info-card">
                <h3>About This Page</h3>
                <p>We analyze listening habits to find the perfect match for your musical taste. Choose a category above, type in a track, album, or artist you currently have on repeat, and generate a custom list of recommendations.</p>
                
                <h3 style="margin-top: 20px;">Quick Search Tips</h3>
                <ul>
                    <li><strong>Spelling & Spaces:</strong> Ensure exact spellings. Avoid trailing accidental spaces at the end of names.</li>
                    <li><strong>Artist Details:</strong> Adding the artist name for songs and albums prevents confusion when titles overlap.</li>
                    <li><strong>Underground Mode:</strong> Use the underground checkbox under Artists to discover hidden musical gems.</li>
                </ul>
            </div>
        </div>
    """
    return page("Music Recommender", body)

@app.route('/search-artist')
def search_artist():
    fallback_artists = [
        "Radiohead", "Tame Impala", "Daft Punk", "Arctic Monkeys", 
        "The Weeknd", "Frank Ocean", "Kendrick Lamar", "Tyler, The Creator", 
        "Lana Del Rey", "Gorillaz", "Billie Eilish", "Kanye West"
    ]
    selected_artists = fetch_trending_artists(3) or random.sample(fallback_artists, 3)
    
    rec_html = ""
    for name in selected_artists:
        img = get_artist_image_from_deezer(name)
        params = urllib.parse.urlencode({"mode": "artist", "query": name})
        rec_html += f"""
        <a href="/recommend?{params}" class="rec-item artist-rec">
            <img src="{img}" alt="{name}">
            <div class="rec-info">
                <span class="rec-title">{name}</span>
            </div>
        </a>
        """

    body = f"""
        <div class="page-center">
            {top_bar("Search Artists")}
            <div class="search-layout">
                <div class="form-card">
                    <p class="tagline">Explore related creators and find underground gems.</p>
                    <form action="/recommend" method="GET" class="search-form" onsubmit="showLoading()">
                        <input type="hidden" name="mode" value="artist">
                        <input type="text" name="query" placeholder="Enter an artist name" required>
                        <label><input type="checkbox" name="include_underground" value="yes"> Dig deeper (Underground artists)</label>
                        <select name="result_count">
                            <option value="10">Top 10 Picks</option>
                            <option value="20" selected>Top 20 Picks</option>
                            <option value="30">Top 30 Picks</option>
                        </select>
                        <button type="submit" id="submit-btn" class="main-btn">Find Matches</button>
                        <div id="loading-spinner" class="spinner"></div>
                    </form>
                </div>
                <div class="rec-sidebar">
                    <h3>Trending Artists</h3>
                    {rec_html}
                </div>
            </div>
        </div>
    """
    return page("Search Artist", body)

@app.route('/search-song')
def search_song():
    fallback_songs = [
        ("Midnight City", "M83"),
        ("Redbone", "Childish Gambino"),
        ("Get Lucky", "Daft Punk"),
        ("The Less I Know The Better", "Tame Impala"),
        ("Blinding Lights", "The Weeknd"),
        ("Pink + White", "Frank Ocean"),
        ("HUMBLE.", "Kendrick Lamar"),
        ("Feel It Still", "Portugal. The Man")
    ]
    selected_songs = fetch_trending_songs(3) or random.sample(fallback_songs, 3)
    
    rec_html = ""
    for title, artist in selected_songs:
        img = get_album_image_for_track(title, artist)
        params = urllib.parse.urlencode({"mode": "song", "query": title, "artist_for_song": artist})
        rec_html += f"""
        <a href="/recommend?{params}" class="rec-item">
            <img src="{img}" alt="{title}">
            <div class="rec-info">
                <span class="rec-title">{title}</span>
                <span class="rec-sub">{artist}</span>
            </div>
        </a>
        """

    body = f"""
        <div class="page-center">
            {top_bar("Search Songs")}
            <div class="search-layout">
                <div class="form-card">
                    <p class="tagline">Find tracks that share the exact same vibe.</p>
                    <form action="/recommend" method="GET" class="search-form" onsubmit="showLoading()">
                        <input type="hidden" name="mode" value="song">
                        <input type="text" name="query" placeholder="Song Title" required>
                        <input type="text" name="artist_for_song" placeholder="Artist Name (Optional)">
                        <select name="result_count">
                            <option value="12">12 Tracks</option>
                            <option value="24" selected>24 Tracks</option>
                        </select>
                        <button type="submit" id="submit-btn" class="main-btn">Find Matches</button>
                        <div id="loading-spinner" class="spinner"></div>
                    </form>
                </div>
                <div class="rec-sidebar">
                    <h3>Trending Tracks</h3>
                    {rec_html}
                </div>
            </div>
        </div>
    """
    return page("Search Song", body)

@app.route('/search_album')
def search_album():
    fallback_albums = [
        ("Rumours", "Fleetwood Mac"),
        ("Illmatic", "Nas"),
        ("Random Access Memories", "Daft Punk"),
        ("Blonde", "Frank Ocean"),
        ("Currents", "Tame Impala"),
        ("Good Kid, M.A.A.D City", "Kendrick Lamar"),
        ("Abbey Road", "The Beatles"),
        ("Thriller", "Michael Jackson")
    ]
    selected_albums = fetch_trending_albums(3) or random.sample(fallback_albums, 3)
    
    rec_html = ""
    for title, artist in selected_albums:
        img = get_album_image_for_search(title, artist)
        params = urllib.parse.urlencode({"mode": "album", "query": title, "artist_for_album": artist})
        rec_html += f"""
        <a href="/recommend?{params}" class="rec-item">
            <img src="{img}" alt="{title}">
            <div class="rec-info">
                <span class="rec-title">{title}</span>
                <span class="rec-sub">{artist}</span>
            </div>
        </a>
        """

    body = f"""
        <div class="page-center">
            {top_bar("Search Albums")}
            <div class="search-layout">
                <div class="form-card">
                    <p class="tagline">Discover full projects with matching moods.</p>
                    <form action="/recommend" method="GET" class="search-form" onsubmit="showLoading()">
                        <input type="hidden" name="mode" value="album">
                        <input type="text" name="query" placeholder="Album Title" required>
                        <input type="text" name="artist_for_album" placeholder="Artist Name (Recommended)">
                        <select name="result_count">
                            <option value="12">12 Albums</option>
                            <option value="24" selected>24 Albums</option>
                        </select>
                        <button type="submit" id="submit-btn" class="main-btn">Find Matches</button>
                        <div id="loading-spinner" class="spinner"></div>
                    </form>
                </div>
                <div class="rec-sidebar">
                    <h3>Featured Albums</h3>
                    {rec_html}
                </div>
            </div>
        </div>
    """
    return page("Search Album", body)

@app.route('/recommend', methods=['GET'])
def recommend():
    query = request.args.get('query', '').strip()
    mode = request.args.get('mode', 'artist')
    artist_for_song = request.args.get('artist_for_song', '').strip()
    artist_for_album = request.args.get('artist_for_album', '').strip()
    result_count = int(request.args.get('result_count', 20))
    
    if not query:
        back_link = "/search-artist" if mode == "artist" else "/search-song"
        return page("Error", f"<div style='width:100%; max-width:860px;'><h1>Oops!</h1><p>Looks like the search was empty.</p><a class='back-link' href='{back_link}'>Try again</a></div>")

    if 'history' not in session:
        session['history'] = [] 
    session['history'].append(f"{query} ({mode.capitalize()})") 
    session.modified = True

    if mode == "artist":
        underground = request.args.get('include_underground', 'no') == 'yes'

        if underground:
            tag_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist={urllib.parse.quote(query)}&api_key={api_key}&format=json"
            tag_response = requests.get(tag_url).json()
            tags_list = tag_response.get('toptags', {}).get('tag', [])
            top_genre = tags_list[0]['name'] if tags_list else None
            
            artists_url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag={urllib.parse.quote(str(top_genre))}&api_key={api_key}&format=json"
            artists_response = requests.get(artists_url).json()
            artists_list = artists_response.get('topartists', {}).get('artist', [])
            underground_picks = artists_list[30 : 30 + result_count] if underground else []
            
            if not underground_picks:
                return page("No results", f"<div style='width:100%; max-width:860px;'><h1>No Results</h1><p>We couldn't find underground matches for '{query}'.</p><a class='back-link' href='/search-artist'>Go Back</a></div>")

            results = ""
            for artist in underground_picks:
                img_url = get_artist_image_from_deezer(artist.get('name'))
                results += f"<div class='result-card artist-card'><img src='{img_url}' alt='Artist'><a href='{artist['url']}' class='title' target='_blank'>{artist['name']}</a><form action='/save_favorites' method='GET' style='margin:0;'><input type='hidden' name='query' value='{artist['name']}'><button class='save-btn' type='submit'>+ Add</button></form></div>"
            return page("Results", f"<div style='width:100%; max-width:1040px;'><h2>Underground Picks based on {query}</h2><ul class='results-grid'>{results}</ul><a class='back-link' href='/search-artist'>Back to Search</a></div>")

        else:
            url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={urllib.parse.quote(query)}&api_key={api_key}&format=json"
            data = requests.get(url).json()
            similar_artists = data.get('similarartists', {}).get('artist', [])[:result_count]
            
            if not similar_artists:
                return page("No results", f"<div style='width:100%; max-width:860px;'><h1>No Results</h1><p>Check the spelling for '{query}' and try again.</p><a class='back-link' href='/search-artist'>Go Back</a></div>")
            
            results = ""
            for artist in similar_artists:
                img_url = get_artist_image_from_deezer(artist.get('name'))
                results += f"<div class='result-card artist-card'><img src='{img_url}' alt='Artist'><a href='{artist['url']}' class='title' target='_blank'>{artist['name']}</a><form action='/save_favorites' method='GET' style='margin:0;'><input type='hidden' name='query' value='{artist['name']}'><button class='save-btn' type='submit'>+ Add</button></form></div>"
            return page("Results", f"<div style='width:100%; max-width:1040px;'><h2>Because you like {query}</h2><ul class='results-grid'>{results}</ul><a class='back-link' href='/search-artist'>Back to Search</a></div>")

    elif mode == "song":
        url = f"http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&track={urllib.parse.quote(query)}&artist={urllib.parse.quote(artist_for_song)}&api_key={api_key}&format=json"
        data = requests.get(url).json()
        similar_tracks = data.get('similartracks', {}).get('track', [])[:result_count]
        
        if not similar_tracks:
            return page("No results", f"<div style='width:100%; max-width:860px;'><h1>No Results</h1><p>We couldn't find matches. Tip: Did you enter the artist name correctly?</p><a class='back-link' href='/search-song'>Go Back</a>")

        results = ""
        for track in similar_tracks:
            art_name, art_url = get_artist_info(track.get('artist'))
            img_url = get_album_image_for_track(track['name'], art_name)
            results += f"<div class='result-card'><img src='{img_url}' alt='Cover'><a href='{track['url']}' class='title' target='_blank'>{track['name']}</a><a href='{art_url}' class='subtitle' target='_blank'>{art_name}</a><form action='/save_favorites' method='GET' style='margin:0;'><input type='hidden' name='query' value='{track['name']} - {art_name}'><button class='save-btn' type='submit'>+ Add</button></form></div>"
        return page("Results", f"<div style='width:100%; max-width:1040px;'><h2>Tracks like {query}</h2><ul class='results-grid'>{results}</ul><a class='back-link' href='/search-song'>Back to Search</a></div>")

    elif mode == "album":
        info_url = f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={api_key}&artist={urllib.parse.quote(artist_for_album)}&album={urllib.parse.quote(query)}&format=json"
        info_data = requests.get(info_url).json()
        
        album_data = info_data.get('album', {})
        tags_info = album_data.get('tags') if isinstance(album_data, dict) else None
        
        if isinstance(tags_info, dict):
            tags_data = tags_info.get('tag', [])
            if isinstance(tags_data, dict):
                tags_data = [tags_data]
        else:
            tags_data = [] 
        
        valid_tags = [t['name'] for t in tags_data if t['name'].lower() != artist_for_album.lower()]
        
        if valid_tags:
            top_tag = random.choice(valid_tags[:3])
            tag_url = f"http://ws.audioscrobbler.com/2.0/?method=tag.gettopalbums&tag={urllib.parse.quote(top_tag)}&api_key={api_key}&format=json"
            tag_data = requests.get(tag_url).json()
            
            album_picks = tag_data.get('albums', {}).get('album', [])
            if not album_picks:
                return page("No results", f"<div style='width:100%; max-width:860px;'><h1>No Results</h1><p>We couldn't match the vibe.</p><a class='back-link' href='/search_album'>Go Back</a></div>")
            
            random.shuffle(album_picks)
            album_picks = album_picks[:result_count]
            
            results = ""
            for album in album_picks:
                img_url = get_image(album, album.get('name'))
                art_name, art_url = get_artist_info(album.get('artist'))
                results += f"<div class='result-card'><img src='{img_url}' alt='Cover'><a href='{album['url']}' class='title' target='_blank'>{album['name']}</a><a href='{art_url}' class='subtitle' target='_blank'>{art_name}</a><form action='/save_favorites' method='GET' style='margin:0;'><input type='hidden' name='query' value='{album['name']} by {art_name}'><button class='save-btn' type='submit'>+ Add</button></form></div>"
                
            return page("Results", f"<div style='width:100%; max-width:1040px;'><h2>Albums with a '{top_tag}' vibe</h2><ul class='results-grid'>{results}</ul><a class='back-link' href='/search_album'>Back to Search</a></div>")

        else:
            similar_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&artist={urllib.parse.quote(artist_for_album)}&api_key={api_key}&format=json"
            similar_data = requests.get(similar_url).json()
            similar_artists = similar_data.get('similarartists', {}).get('artist', [])[:result_count]

            if not similar_artists:
                 return page("No results", f"<div style='width:100%; max-width:860px;'><h1>No Results</h1><p>Check spelling and try again.</p><a class='back-link' href='/search_album'>Go Back</a></div>")

            results = ""
            for artist in similar_artists:
                a_url = f"http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist={urllib.parse.quote(artist['name'])}&api_key={api_key}&format=json"
                a_data = requests.get(a_url).json()
                album_list = a_data.get('topalbums', {}).get('album', [])
                
                if album_list:
                    top_album = random.choice(album_list[:3])
                    img_url = get_image(top_album, top_album.get('name'))
                    art_name, art_url = get_artist_info(artist)
                    results += f"<div class='result-card'><img src='{img_url}' alt='Cover'><a href='{top_album['url']}' class='title' target='_blank'>{top_album['name']}</a><a href='{art_url}' class='subtitle' target='_blank'>{art_name}</a><form action='/save_favorites' method='GET' style='margin:0;'><input type='hidden' name='query' value='{top_album['name']} by {art_name}'><button class='save-btn' type='submit'>+ Add</button></form></div>"

            return page("Results", f"<div style='width:100%; max-width:1040px;'><h2>Albums from similar artists</h2><ul class='results-grid'>{results}</ul><a class='back-link' href='/search_album'>Back to Search</a></div>")

@app.route('/history')
def history():
    history_list = session.get('history', [])
    header = top_bar("Recently Searched")
    if not history_list:
        return page("History", f"<div style='width:100%; max-width:1040px;'>{header}<p class='tagline'>No search history found.</p></div>")
    results = ""
    for item in reversed(history_list):
        results += f"<div style='padding: 14px 0; border-bottom: 1px solid #2c2c2e;'>{item}</div>"
    return page("Search History", f"<div style='width:100%; max-width:1040px;'>{header}<div style='max-width: 600px;'>{results}</div></div>")

@app.route('/save_favorites')
def save_favorites():
    query = request.args.get('query', '') 
    if query:
        with open('favorites.txt', 'a') as f:
            f.write(query + '\n')
    return redirect(request.referrer or url_for('landing'))

@app.route('/favorites')
def favorites():
    try:
        with open('favorites.txt', 'r') as f:
            favorites_list = f.read().splitlines()
    except FileNotFoundError:
        favorites_list = []

    header = top_bar("Library")
    if not favorites_list:
        return page("Favorites", f"<div style='width:100%; max-width:1040px;'>{header}<p class='tagline'>No favorites added yet.</p></div>")
    
    results = ""
    for item in reversed(favorites_list):
        results += f"<div style='padding: 14px 0; border-bottom: 1px solid #2c2c2e; display: flex; align-items: center; gap: 12px;'><svg style='width:20px;height:20px;fill:var(--theme-accent)' viewBox='0 0 24 24'><path d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/></svg> {item}</div>"
    return page("Favorites", f"<div style='width:100%; max-width:1040px;'>{header}<div style='max-width: 600px;'>{results}</div></div>")

if __name__ == '__main__':
    app.run(debug=True)