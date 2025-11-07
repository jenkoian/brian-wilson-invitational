import streamlit as st

st.title("🎵Brian Wilson Invitational Stats")

pg = st.navigation(
    [
        "leaderboard.py",
        "song_popularity.py",
        "song_unpopularity.py",
        "artist_popularity.py",
        "artist_unpopularity.py",
        "meh_songs.py",
        "point_breakdown_heatmap.py",
        "vote_breakdown_heatmap.py",
        "voting_by_playlist_position.py",
        "votes_given.py",
        "wordclouds.py",
        "bit_of_fun.py",
    ]
)
pg.run()
