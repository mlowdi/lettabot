import re

def fmt_duration_ms(ms: int) -> str:
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    return f"{minutes}:{seconds:02d}"

def fmt_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)

def parse_spotify_id(input_str: str, expected_type: str | None = None) -> str:
    detected_type = None
    
    if "open.spotify.com" in input_str:
        match = re.search(r"/(track|album|artist|playlist)/([a-zA-Z0-9]+)", input_str)
        if match:
            detected_type = match.group(1)
            extracted_id = match.group(2)
        else:
            return input_str
    elif input_str.startswith("spotify:"):
        parts = input_str.split(":")
        if len(parts) >= 3:
            detected_type = parts[1]
            extracted_id = parts[2]
        else:
            return input_str
    else:
        return input_str
    
    if expected_type and detected_type and detected_type != expected_type:
        raise ValueError(f"Expected a {expected_type} URI but got {detected_type}: {input_str}")
    
    return extracted_id

def fmt_track(track_dict: dict) -> str:
    name = track_dict.get("name", "Unknown Track")
    artists = ", ".join([a.get("name", "Unknown Artist") for a in track_dict.get("artists", [])])
    uri = track_dict.get("uri", "Unknown URI")
    parts = [f'"{ name }" by {artists}']
    album_name = track_dict.get("album", {}).get("name")
    if album_name:
        parts.append(f'[album: {album_name}]')
    parts.append(f'({uri})')
    duration = track_dict.get("duration_ms")
    if duration:
        parts.append(f'[{fmt_duration_ms(duration)}]')
    return " ".join(parts)

def fmt_album(album_dict: dict) -> str:
    name = album_dict.get("name", "Unknown Album")
    artists = ", ".join([a.get("name", "Unknown Artist") for a in album_dict.get("artists", [])])
    uri = album_dict.get("uri", "Unknown URI")
    parts = [f'"{ name }" by {artists}']
    release_date = album_dict.get("release_date")
    if release_date:
        parts.append(f'({release_date[:4]})')
    total_tracks = album_dict.get("total_tracks")
    if total_tracks:
        parts.append(f'[{total_tracks} tracks]')
    parts.append(f'({uri})')
    return " ".join(parts)

def fmt_artist(artist_dict: dict) -> str:
    name = artist_dict.get("name", "Unknown Artist")
    uri = artist_dict.get("uri", "Unknown URI")
    parts = [f'"{ name }"']
    genres = artist_dict.get("genres", [])
    if genres:
        parts.append(f'[genres: {", ".join(genres)}]')
    followers = artist_dict.get("followers", {}).get("total")
    if followers is not None and followers > 0:
        parts.append(f'[followers: {fmt_number(followers)}]')
    parts.append(f'({uri})')
    return " ".join(parts)

def fmt_playlist(playlist_dict: dict) -> str:
    name = playlist_dict.get("name", "Unknown Playlist")
    owner = playlist_dict.get("owner", {}).get("display_name", "Unknown Owner")
    uri = playlist_dict.get("uri", "Unknown URI")
    parts = [f'"{ name }" by {owner}']
    track_count = playlist_dict.get("tracks", {}).get("total")
    if track_count is not None:
        parts.append(f'[{track_count} tracks]')
    parts.append(f'({uri})')
    return " ".join(parts)
