import zipfile
import duckdb
import os
import shutil
import time
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pylast


def retry_api_call(max_retries=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        print(f"Failed after {max_retries} attempts: {e}")
                        raise
                    print(f"Error encountered: {e}. Retrying in {delay}s... ({retries}/{max_retries})")
                    time.sleep(delay)
        return wrapper
    return decorator


def add_genre_spotify(table_name: str):
    query = f"""
    select "Spotify URI",
    from {table_name}
    """

    songs = con.execute(query).fetchall()

    @retry_api_call(max_retries=5, delay=3)
    def fetch_spotify_data(uri):
        song = sp.track(uri)
        artist_ids = [artist['id'] for artist in song['artists']]
        artists = sp.artists(artist_ids)
        return song, artists

    for uri in songs:
        try:
            song, artists = fetch_spotify_data(uri[0])
            print(f"Getting genre for {song['name']} by {song['artists'][0]['name']}")

            genres = [artist['genres'] for artist in artists['artists']]

            genre = genres[0]
            query = f"UPDATE {table_name} SET spotify_genres = {genre} WHERE \"Spotify URI\" = '{uri[0]}'"
            con.execute(query)
        except Exception as e:
            print(f"Skipping {uri[0]} due to persistent error.")


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

    @retry_api_call(max_retries=5, delay=2)
    def fetch_lastfm_data(artist, title):
        track = lf.get_track(artist, title)
        return track, track.get_top_tags()

    for song in songs:
        try:
            track, tags = fetch_lastfm_data(song[0], song[1])

            print(f"Getting genre for {track}")

            genres = [tag.item.get_name().lower() for tag in tags[:2]]

            query = f"UPDATE {table_name} SET lastfm_genres = {genres} WHERE \"Spotify URI\" = '{song[2]}'"
            con.execute(query)
        except Exception as e:
            print(f"Skipping {song[0]} - {song[1]} due to Last.fm error.")


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