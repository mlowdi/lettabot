import typer
from spotiboti.commands.auth_cmd import app as auth_app
from spotiboti.commands.catalog import app as catalog_app
from spotiboti.commands.library import app as library_app

app = typer.Typer(
    name="spotiboti",
    help="AI agent tool for Spotify library management. Use 'catalog' for browsing Spotify, 'library' for managing your saved items.",
    no_args_is_help=True,
)

app.add_typer(auth_app, name="auth", help="Authentication setup and status")
app.add_typer(catalog_app, name="catalog", help="Browse Spotify catalog (uses client credentials)")
app.add_typer(library_app, name="library", help="Manage your Spotify library (uses OAuth)")

if __name__ == "__main__":
    app()
