import zipfile
import duckdb
import os
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def add_genre(table_name: str):
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
        query = f"UPDATE {table_name} SET genres = {genre} WHERE \"Spotify URI\" = '{uri[0]}'"
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

# Let's add genre information for all submissions and votes
print('Adding genre information...')

con.execute("ALTER TABLE submissions ADD COLUMN genres VARCHAR[]")

add_genre('submissions')
# When there are lots of votes, this takes a long time and will likely hit rate limits
#add_genre('votes')

print('Building UI database...')
con = duckdb.connect(database='bwi_ui.duckdb')

for file in ['competitors.csv', 'rounds.csv', 'submissions.csv', 'votes.csv']:
    query = f"CREATE OR REPLACE TABLE {file.replace('.csv', '')} AS SELECT * FROM read_csv('data/{file}')"
    con.execute(query)


add_genre('submissions')