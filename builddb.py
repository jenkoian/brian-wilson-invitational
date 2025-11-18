import zipfile
import duckdb
import os
import shutil
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pylast


def add_genre_spotify(table_name: str):
    query = f"""
    select "Spotify URI",
    from {table_name}
    """

    songs = con.execute(query).fetchall()

    for uri in songs:
        song = sp.track(uri[0])

        print(f"Getting genre for {song['name']} by {song['artists'][0]['name']} ({song['artists'][0]['id']})")

        artist_ids = [artist['id'] for artist in song['artists']]
        artists = sp.artists(artist_ids)

        genres = [artist['genres'] for artist in artists['artists']]

        genre = genres[0]
        query = f"UPDATE {table_name} SET spotify_genres = {genre} WHERE \"Spotify URI\" = '{uri[0]}'"
        con.execute(query)


def add_genre_lastfm(table_name: str):
    if table_name == 'submissions':
        query = f"""
        select "Artist(s)", "Title", "Spotify URI"
        from {table_name}
        """
    else:
        query = f"""
        select s."Artist(s)", s."Title", s."Spotify URI"
        from submissions s
        join {table_name} t on s."Spotify URI" = t."Spotify URI"
        """

    songs = con.execute(query).fetchall()

    for song in songs:
        track = lf.get_track(song[0], song[1])
        tags = track.get_top_tags()

        print(f"Getting genre for {track}")

        genres = [tag.item.get_name().lower() for tag in tags[:2]]

        query = f"UPDATE {table_name} SET lastfm_genres = {genres} WHERE \"Spotify URI\" = '{song[2]}'"
        con.execute(query)


print('Unzipping export.zip...')
with zipfile.ZipFile('export.zip', 'r') as zip_ref:
    zip_ref.extractall('data/')
    zip_ref.close()


print('Building database...')
con = duckdb.connect(database='bwi.duckdb')

for file in ['competitors.csv', 'rounds.csv', 'submissions.csv', 'votes.csv']:
    query = f"CREATE OR REPLACE TABLE {file.replace('.csv', '')} AS SELECT * FROM read_csv('data/{file}')"
    con.execute(query)

load_dotenv()

sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
)

lf = pylast.LastFMNetwork(
    api_key=os.getenv('LAST_FM_API_KEY'),
    api_secret=os.getenv('LAST_FM_API_SECRET'),
)

# Let's add genre information for all submissions and votes
print('Adding genre information...')

con.execute("ALTER TABLE submissions ADD COLUMN spotify_genres VARCHAR[]")
con.execute("ALTER TABLE submissions ADD COLUMN lastfm_genres VARCHAR[]")

add_genre_spotify('submissions')
add_genre_lastfm('submissions')
# When there are lots of votes, this takes a long time and will likely hit rate limits
#add_genre('votes')

print('Building UI database...')
shutil.copyfile('bwi.duckdb', 'bwi_ui.duckdb')