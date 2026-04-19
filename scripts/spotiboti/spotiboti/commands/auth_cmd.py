import typer
from spotiboti.config import save_config, load_config, get_catalog_cache_path, get_library_cache_path, DEFAULT_REDIRECT_URI
from spotiboti.auth import get_library_client
from pathlib import Path

app = typer.Typer()

@app.command()
def setup(
    client_id: str = typer.Option(..., prompt=True, help="Spotify Client ID"),
    client_secret: str = typer.Option(..., prompt=True, hide_input=True, help="Spotify Client Secret"),
    redirect_uri: str = typer.Option(DEFAULT_REDIRECT_URI, prompt=True, help="Spotify Redirect URI")
):
    """Save Spotify credentials and trigger OAuth login."""
    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }
    save_config(config)
    typer.echo("Config saved. Opening browser for library authorization...")
    try:
        client = get_library_client()
        user = client.me()
        config["market"] = user.get("country", "US")
        save_config(config)
        typer.echo(f"Success! Authorized as {user['display_name']} ({user['id']}) [market: {config['market']}]")
    except Exception as e:
        typer.echo(f"Error during authorization: {e}", err=True)

@app.command()
def status():
    """Show authentication and config status."""
    config = load_config()
    client_id = config.get("client_id")
    
    typer.echo(f"Config: {'FOUND' if client_id else 'MISSING'}")

    market = config.get("market")
    typer.echo(f"Market: {market if market else 'NOT SET'}")
    
    catalog_cache = Path(get_catalog_cache_path())
    typer.echo(f"Catalog Token: {'CACHED' if catalog_cache.exists() else 'NOT FOUND'}")
    
    library_cache = Path(get_library_cache_path())
    typer.echo(f"Library Token: {'CACHED' if library_cache.exists() else 'NOT FOUND'}")
