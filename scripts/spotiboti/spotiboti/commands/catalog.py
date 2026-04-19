import logging
import typer
from typing import Optional
from spotiboti.auth import get_catalog_client, get_library_client
from spotiboti.config import get_market

logging.getLogger("spotipy").setLevel(logging.CRITICAL)
from spotiboti.formatting import (
    fmt_track, fmt_album, fmt_artist, fmt_playlist, parse_spotify_id
)

app = typer.Typer()

@app.command()
def search(
    query: str,
    type: str = typer.Option("track", help="Type of item to search for: track, album, artist, playlist"),
    limit: int = typer.Option(10, help="Number of results to return (max 50)"),
    market: str = typer.Option(None, help="Market/country code (default: from config)")
):
    """Search Spotify catalog."""
    client = get_catalog_client()
    resolved_market = market or get_market()
    results = client.search(q=query, limit=limit, type=type, market=resolved_market)
    
    key = f"{type}s"
    if key not in results:
        typer.echo(f"No results found for type '{type}'")
        return

    items = results[key]["items"]
    for item in items:
        if type == "track":
            typer.echo(fmt_track(item))
        elif type == "album":
            typer.echo(fmt_album(item))
        elif type == "artist":
            typer.echo(fmt_artist(item))
        elif type == "playlist":
            typer.echo(fmt_playlist(item))

@app.command()
def artist(
    uri_or_id: str,
    market: str = typer.Option(None, help="Market/country code (default: from config)")
):
    """Show artist info, top tracks, and latest albums."""
    client = get_catalog_client()
    artist_id = parse_spotify_id(uri_or_id, expected_type="artist")
    
    artist_data = client.artist(artist_id)
    typer.echo(f"--- Artist ---")
    typer.echo(fmt_artist(artist_data))
    
    typer.echo(f"\n--- Top Tracks ---")
    resolved_market = market or get_market()
    try:
        top_tracks = client.artist_top_tracks(artist_id, market=resolved_market) if resolved_market else client.artist_top_tracks(artist_id)
    except Exception:
        try:
            lib_client = get_library_client()
            top_tracks = lib_client.artist_top_tracks(artist_id, market=resolved_market) if resolved_market else lib_client.artist_top_tracks(artist_id)
        except Exception:
            top_tracks = None
            typer.echo("(top tracks unavailable)")
    if top_tracks:
        for track in top_tracks["tracks"][:5]:
            typer.echo(fmt_track(track))
        
    typer.echo(f"\n--- Latest Albums ---")
    albums = client.artist_albums(artist_id, album_type="album", limit=5)
    for album in albums["items"]:
        typer.echo(fmt_album(album))

@app.command()
def album(
    uri_or_id: str,
    limit: int = typer.Option(50, help="Number of tracks to show"),
    offset: int = typer.Option(0, help="Index of first track to show")
):
    """Show album info and track listing."""
    client = get_catalog_client()
    album_id = parse_spotify_id(uri_or_id, expected_type="album")
    resolved_market = get_market()
    
    album_data = client.album(album_id, market=resolved_market)
    typer.echo(fmt_album(album_data))
    
    typer.echo(f"\n--- Tracks ---")
    tracks = client.album_tracks(album_id, limit=limit, offset=offset, market=resolved_market)
    for track in tracks["items"]:
        if "artists" not in track:
            track["artists"] = album_data["artists"]
        if "album" not in track:
            track["album"] = album_data
        typer.echo(fmt_track(track))

@app.command()
def track(uri_or_id: str):
    """Show track details and audio features."""
    client = get_catalog_client()
    track_id = parse_spotify_id(uri_or_id, expected_type="track")
    resolved_market = get_market()
    
    track_data = client.track(track_id, market=resolved_market)
    typer.echo(fmt_track(track_data))
    
    try:
        features = client.audio_features([track_id])[0]
    except Exception:
        try:
            lib_client = get_library_client()
            features = lib_client.audio_features([track_id])[0]
        except Exception:
            features = None
    if features:
        typer.echo(f"Features: bpm={features['tempo']:.0f} key={features['key']} danceability={features['danceability']} energy={features['energy']}")
