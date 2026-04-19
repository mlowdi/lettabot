import typer
from spotiboti.auth import get_library_client
from spotiboti.formatting import fmt_track, fmt_album, fmt_playlist, parse_spotify_id

app = typer.Typer()

@app.command()
def saved_tracks(
    limit: int = typer.Option(20, help="Number of tracks to return"),
    offset: int = typer.Option(0, help="Index of the first track to return")
):
    """List your saved tracks."""
    client = get_library_client()
    results = client.current_user_saved_tracks(limit=limit, offset=offset)
    total = results["total"]
    typer.echo(f"Total: {total} saved tracks (showing {len(results['items'])}, offset {offset})")
    for item in results["items"]:
        typer.echo(fmt_track(item["track"]))

@app.command()
def saved_albums(
    limit: int = typer.Option(20, help="Number of albums to return"),
    offset: int = typer.Option(0, help="Index of the first album to return")
):
    """List your saved albums."""
    client = get_library_client()
    results = client.current_user_saved_albums(limit=limit, offset=offset)
    total = results["total"]
    typer.echo(f"Total: {total} saved albums (showing {len(results['items'])}, offset {offset})")
    for item in results["items"]:
        typer.echo(fmt_album(item["album"]))

@app.command()
def save_tracks(
    uri_or_ids: list[str] = typer.Argument(..., help="Track URIs or IDs to save")
):
    """Save tracks to your library."""
    client = get_library_client()
    ids = [parse_spotify_id(uid) for uid in uri_or_ids]
    client.current_user_saved_tracks_add(ids)
    typer.echo(f"Saved {len(ids)} tracks to library.")

@app.command()
def remove_tracks(
    uri_or_ids: list[str] = typer.Argument(..., help="Track URIs or IDs to remove")
):
    """Remove tracks from your library."""
    client = get_library_client()
    ids = [parse_spotify_id(uid) for uid in uri_or_ids]
    client.current_user_saved_tracks_delete(ids)
    typer.echo(f"Removed {len(ids)} tracks from library.")

@app.command()
def save_albums(
    uri_or_ids: list[str] = typer.Argument(..., help="Album URIs or IDs to save")
):
    """Save albums to your library."""
    client = get_library_client()
    ids = [parse_spotify_id(uid) for uid in uri_or_ids]
    client.current_user_saved_albums_add(ids)
    typer.echo(f"Saved {len(ids)} albums to library.")

@app.command()
def remove_albums(
    uri_or_ids: list[str] = typer.Argument(..., help="Album URIs or IDs to remove")
):
    """Remove albums from your library."""
    client = get_library_client()
    ids = [parse_spotify_id(uid) for uid in uri_or_ids]
    client.current_user_saved_albums_delete(ids)
    typer.echo(f"Removed {len(ids)} albums from library.")

@app.command()
def playlists(
    limit: int = typer.Option(20, help="Number of playlists to return"),
    offset: int = typer.Option(0, help="Index of the first playlist to return")
):
    """List your playlists."""
    client = get_library_client()
    results = client.current_user_playlists(limit=limit, offset=offset)
    total = results["total"]
    typer.echo(f"Total: {total} playlists (showing {len(results['items'])}, offset {offset})")
    for item in results["items"]:
        typer.echo(fmt_playlist(item))

@app.command()
def playlist(
    uri_or_id: str = typer.Argument(..., help="Playlist URI or ID"),
    limit: int = typer.Option(50, help="Number of tracks to return"),
    offset: int = typer.Option(0, help="Index of the first track to return")
):
    """Show playlist details and tracks."""
    client = get_library_client()
    playlist_id = parse_spotify_id(uri_or_id, expected_type="playlist")
    info = client.playlist(playlist_id)
    typer.echo(fmt_playlist(info))
    
    results = client.playlist_items(playlist_id, limit=limit, offset=offset)
    typer.echo(f"\nTracks (Total: {results['total']}, showing {len(results['items'])}, offset {offset}):")
    for item in results["items"]:
        if item.get("track"):
            typer.echo(fmt_track(item["track"]))

@app.command()
def playlist_add(
    playlist_uri_or_id: str = typer.Argument(..., help="Playlist URI or ID"),
    uri_or_ids: list[str] = typer.Argument(..., help="Track URIs or IDs to add")
):
    """Add tracks to a playlist."""
    client = get_library_client()
    playlist_id = parse_spotify_id(playlist_uri_or_id, expected_type="playlist")
    # Playlist add_items expects URIs
    items = []
    for uid in uri_or_ids:
        track_id = parse_spotify_id(uid)
        items.append(f"spotify:track:{track_id}")
    client.playlist_add_items(playlist_id, items)
    typer.echo(f"Added {len(items)} tracks to playlist.")

@app.command()
def playlist_remove(
    playlist_uri_or_id: str = typer.Argument(..., help="Playlist URI or ID"),
    uri_or_ids: list[str] = typer.Argument(..., help="Track URIs or IDs to remove")
):
    """Remove all occurrences of tracks from a playlist."""
    client = get_library_client()
    playlist_id = parse_spotify_id(playlist_uri_or_id, expected_type="playlist")
    # Playlist remove_all_occurrences_of_items expects URIs
    items = []
    for uid in uri_or_ids:
        track_id = parse_spotify_id(uid)
        items.append(f"spotify:track:{track_id}")
    client.playlist_remove_all_occurrences_of_items(playlist_id, items)
    typer.echo(f"Removed {len(items)} tracks from playlist.")

@app.command()
def playlist_create(
    name: str = typer.Argument(..., help="Name of the new playlist"),
    description: str = typer.Option("", help="Description for the playlist"),
    public: bool = typer.Option(True, help="Whether the playlist is public")
):
    """Create a new playlist."""
    client = get_library_client()
    user_id = client.me()["id"]
    new_playlist = client.user_playlist_create(user_id, name, public=public, description=description)
    typer.echo("Created new playlist:")
    typer.echo(fmt_playlist(new_playlist))
