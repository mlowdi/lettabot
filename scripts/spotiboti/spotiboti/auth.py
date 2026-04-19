import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotiboti.config import load_config, get_catalog_cache_path, get_library_cache_path, DEFAULT_REDIRECT_URI

def get_catalog_client() -> spotipy.Spotify:
    config = load_config()
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")

    if not client_id or not client_secret:
        raise ValueError("Missing client_id or client_secret in config. Run 'spotiboti auth setup'.")

    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
        cache_handler=spotipy.cache_handler.CacheFileHandler(cache_path=get_catalog_cache_path())
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def get_library_client() -> spotipy.Spotify:
    config = load_config()
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    redirect_uri = config.get("redirect_uri", DEFAULT_REDIRECT_URI)

    if not client_id or not client_secret:
        raise ValueError("Missing client_id or client_secret in config. Run 'spotiboti auth setup'.")

    scope = (
        "user-read-private "
        "user-library-read user-library-modify "
        "playlist-read-private playlist-read-collaborative "
        "playlist-modify-public playlist-modify-private"
    )

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_handler=spotipy.cache_handler.CacheFileHandler(cache_path=get_library_cache_path()),
        open_browser=True
    )
    return spotipy.Spotify(auth_manager=auth_manager)
