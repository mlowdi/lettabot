---
name: spotiboti
description: Use when the user asks you to search, browse, or manage their Spotify library — searching for music, saving tracks/albums, managing playlists, etc.
---

# spotiboti — Spotify Library Management Tool

## Overview
A CLI tool for managing Spotify library with two modes:
- **Catalog Mode:** Uses Client Credentials flow for searching and browsing Spotify without user authentication.
- **Library Mode:** Uses OAuth flow for managing a user's library, including saved tracks, albums, and playlists.

## Setup
To initialize the tool, you'll need a Spotify Client ID and Client Secret from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

- **Authentication Setup:**
  `uv run spotiboti auth setup --client-id <ID> --client-secret <SECRET> --redirect-uri <URI>`
  (Note: You can omit flags to be prompted for these values.)
- **Check Status:**
  `uv run spotiboti auth status`

## Catalog Commands (no user auth needed)
Browse the Spotify catalog. All commands accept a Spotify URI, URL, or plain ID.

- **Search for content:**
  `uv run spotiboti catalog search "query" --type <track|album|artist|playlist> --limit <number>`
- **View Artist details (top tracks & latest albums):**
  `uv run spotiboti catalog artist <URI_OR_ID>`
- **View Album details (track listing):**
  `uv run spotiboti catalog album <URI_OR_ID>`
- **View Track details (includes audio features):**
  `uv run spotiboti catalog track <URI_OR_ID>`

## Library Commands (requires OAuth)
Manage your personal Spotify library and playlists.

- **List Saved Content:**
  `uv run spotiboti library saved-tracks [--limit <N>] [--offset <O>]`
  `uv run spotiboti library saved-albums [--limit <N>] [--offset <O>]`
- **Save/Remove Tracks:**
  `uv run spotiboti library save-tracks <URI1> <URI2>...`
  `uv run spotiboti library remove-tracks <URI1> <URI2>...`
- **Save/Remove Albums:**
  `uv run spotiboti library save-albums <URI1> <URI2>...`
  `uv run spotiboti library remove-albums <URI1> <URI2>...`
- **Manage Playlists:**
  `uv run spotiboti library playlists` (List your playlists)
  `uv run spotiboti library playlist <URI_OR_ID>` (View details)
  `uv run spotiboti library playlist-create "Name" [--description "text"] [--public|--private]`
  `uv run spotiboti library playlist-add <PLAYLIST_URI> <TRACK_URI1> <TRACK_URI2>...`
  `uv run spotiboti library playlist-remove <PLAYLIST_URI> <TRACK_URI1> <TRACK_URI2>...`

## Output Format
The tool uses a compact, parseable output format:

- **Tracks:** `"Track Name" by Artist1, Artist2 [album: Album Name] (spotify:track:xxx) [3:45]`
- **Albums:** `"Album Name" by Artist (YYYY) [N tracks] (spotify:album:xxx)`
- **Artists:** `"Artist Name" [genres: rock, pop] [followers: 1.2M] (spotify:artist:xxx)`
- **Playlists:** `"Playlist Name" by Owner [N tracks] (spotify:playlist:xxx)`

Note: Fields like genres, followers, album, and duration are omitted when not available (e.g. in search results which return simplified objects).

## ID Formats
All commands accept the following formats for IDs:
1. **Plain ID:** `6rqhFgbbKwnb9MLmUQDhG6`
2. **Spotify URI:** `spotify:track:6rqhFgbbKwnb9MLmUQDhG6`
3. **Spotify URL:** `https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6`

## Common Workflows

### Browse and Save
1. Search for an artist: `uv run spotiboti catalog search "The Beatles" --type artist`
2. View artist's albums: `uv run spotiboti catalog artist <ARTIST_URI>`
3. View tracks in an album: `uv run spotiboti catalog album <ALBUM_URI>`
4. Save selected tracks: `uv run spotiboti library save-tracks <TRACK_URI1> <TRACK_URI2>`

### Playlist Management
1. Create a playlist: `uv run spotiboti library playlist-create "My New Jam"`
2. Search for a track: `uv run spotiboti catalog search "Song Name" --type track`
3. Add it to the playlist: `uv run spotiboti library playlist-add <PLAYLIST_URI> <TRACK_URI>`

## Tips
- **Use Catalog First:** Always use `catalog` commands for browsing. It uses separate rate limits and doesn't require user OAuth for initial discovery.
- **Pagination:** Use `--limit` (default 10, max 50) and `--offset` for navigating large sets of results (applies to search and library listing commands).
- **Chaining:** URIs from any command output can be used directly as input for subsequent library or catalog commands.
