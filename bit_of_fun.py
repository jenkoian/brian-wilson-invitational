import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

con = duckdb.connect(database='bwi.duckdb')

def create_radar_chart(df_long: pd.DataFrame, id_var: str = 'submitter'):
    max_count = df_long['Count'].max()

    # Create the Plotly Radar Chart
    fig = px.line_polar(
        df_long,
        r='Count',
        theta='genre_name',
        line_close=True,
        range_r=[0, max_count * 1.1],
        title=f"Submitted genres for {competitor}" if id_var == 'submitter' else f"Voted genres for {competitor}",
        template='plotly_white'
    )

    # Customize the layout
    fig.update_traces(fill='toself') # Fills the area inside the line

    return fig

st.subheader("Bit of fun")

query = """
select Name
from competitors
order by Name asc
"""
competitors = con.execute(query).df()

with st.container(border=True):
    competitor = st.selectbox("Competitor", competitors['Name'], index=None, placeholder="Select competitor...")

query = """
WITH combined_genres AS (
    SELECT
        c.Name AS submitter,
        flatten(LIST(s.spotify_genres || s.lastfm_genres)) AS all_unique_genres
    FROM
        submissions s
    JOIN
        competitors c ON s."Submitter ID" = c.ID
    GROUP BY
        c.Name
)
SELECT
    submitter,
    UNNEST(cg.all_unique_genres) AS genre_name
FROM
    combined_genres cg
WHERE cg.submitter = ?;
"""

df = con.execute(query, [competitor]).df()

min_count_filter = st.slider(
    "**Minimum Submissions Per Genre (Filter Out Low Counts):**",
    min_value=1,
    max_value=5,
    value=2, # Defaulting to 2 to filter out single submissions
    step=1
)

df_genre_counts = df.groupby('genre_name').size().reset_index(name='Count')

df_genre_counts = df_genre_counts[df_genre_counts['Count'] >= min_count_filter].copy()

if df_genre_counts.empty:
    st.warning(f"⚠️ **{competitor}** has no genres with a submission count of {min_count_filter} or more.")
else:
    radar_fig = create_radar_chart(df_genre_counts, 'submitter')
    st.plotly_chart(radar_fig, use_container_width=True)

# Voted genres
query = """
WITH combined_genres AS (
    SELECT
        c.Name AS voter,
        flatten(LIST(s.spotify_genres || s.lastfm_genres)) AS all_unique_genres
    FROM
        votes v
    JOIN
        competitors c ON v."Voter ID" = c.ID
    JOIN 
        submissions s on v."Spotify URI" = s."Spotify URI"
    GROUP BY
        c.Name
)
SELECT
    voter,
    UNNEST(cg.all_unique_genres) AS genre_name,    
FROM
    combined_genres cg
WHERE cg.voter = ?;
"""

df = con.execute(query, [competitor]).df()

min_count_filter = st.slider(
    "**Minimum Votes Per Genre (Filter Out Low Counts):**",
    min_value=1,
    max_value=5,
    value=2, # Defaulting to 2 to filter out single submissions
    step=1
)

df_genre_counts = df.groupby('genre_name').size().reset_index(name='Count')

df_genre_counts = df_genre_counts[df_genre_counts['Count'] >= min_count_filter].copy()

if df_genre_counts.empty:
    st.warning(f"⚠️ **{competitor}** has no genres with a votes count of {min_count_filter} or more.")
else:
    radar_fig = create_radar_chart(df_genre_counts, 'voter')
    st.plotly_chart(radar_fig, use_container_width=True)

# st.subheader("Your voted genres")
# df_vertical_table = df_counts.T
# df_vertical_table.reset_index(inplace=True)
# df_vertical_table.columns = ['genre_name', 'Count']
# df_vertical_table.rename(columns={'genre_name': 'Genre'}, inplace=True)
# df_vertical_table.sort_values(by='Count', ascending=False, inplace=True)
#
# st.dataframe(df_vertical_table, hide_index=True)

# Other stuff

query = """
with round_songs as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' - ', s.title) as song, 
  s."Spotify URI" as spotify_uri,
  SUM(v."Points Assigned") as score
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  GROUP BY round, song, spotify_uri
),
round_winning_songs as (
  select round, MAX_BY(song, score) as song, MAX_BY(spotify_uri, score) as spotify_uri
  from round_songs
  group by round
)
select COUNT(1) as times, SUM(v."Points Assigned") as votes
from round_winning_songs rws 
join votes v on rws.spotify_uri = v."Spotify URI"
join competitors c on v."Voter ID" = c.ID
where v."Points Assigned" > 0  
and c."name" = ?;
"""

df = con.execute(query, [competitor]).df()

st.metric("How often you (up)voted the winning song", df['times'])

if int(df['times'][0]) > 0:
  votes = int(df['votes'][0])
  votes_str = 'votes' if votes != 1 else 'vote'
  st.caption(f"You dished out {votes} {votes_str} to the winning songs in total")

query = """
with round_songs as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' - ', s.title) as song, 
  s."Spotify URI" as spotify_uri,
  SUM(v."Points Assigned") as score
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  GROUP BY round, song, spotify_uri
),
round_winning_songs as (
  select round, MAX_BY(song, score) as song, MAX_BY(spotify_uri, score) as spotify_uri
  from round_songs
  group by round
)
select COUNT(1) as times, SUM(v."Points Assigned") as votes
from round_winning_songs rws 
join votes v on rws.spotify_uri = v."Spotify URI"
join competitors c on v."Voter ID" = c.ID
where v."Points Assigned" < 0  
and c."name" = ?;
"""

df = con.execute(query, [competitor]).df()

st.metric("How often you (down)voted the winning song", df['times'])

if int(df['times'][0]) > 0:
  votes = int(df['votes'][0])
  votes_str = 'votes' if votes != 1 else 'vote'
  st.caption(f"You dished out {votes} {votes_str} to the winning songs in total")

query = """
with round_songs as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' - ', s.title) as song, 
  s."Spotify URI" as spotify_uri,
  SUM(v."Points Assigned") as score
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  GROUP BY round, song, spotify_uri
),
round_losing_songs as (
  select round, MIN_BY(song, score) as song, MIN_BY(spotify_uri, score) as spotify_uri
  from round_songs
  group by round
)
select COUNT(1) as times, SUM(v."Points Assigned") as votes
from round_losing_songs rws 
join votes v on rws.spotify_uri = v."Spotify URI"
join competitors c on v."Voter ID" = c.ID
where v."Points Assigned" > 0  
and c."name" = ?;
"""

df = con.execute(query, [competitor]).df()

st.metric("How often you (up)voted the losing song", df['times'])

if int(df['times'][0]) > 0:
  votes = int(df['votes'][0])
  votes_str = 'votes' if votes != 1 else 'vote'
  st.caption(f"You dished out {votes} {votes_str} to the losing songs in total")

query = """
WITH comments_no_points as (
  SELECT cv.Name as voter, cs.Name as submitter, r."name" as round, 
  CONCAT(s."Artist(s)", ' - ', s.title) as song,
  v."Points Assigned"::INTEGER as points,
  v."Comment" as comment,
  LENGTH(v."Comment") as comment_length
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN competitors cs ON s."Submitter ID" = cs.ID
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  JOIN competitors cv ON v."Voter ID" = cv.ID
  WHERE v."Comment" is not null
  AND points = 0
)
SELECT COUNT(1) as times, MAX_BY(comment, comment_length) as longest_comment
FROM comments_no_points
WHERE voter = ?;
"""

df = con.execute(query, [competitor]).df()

if int(df['times'][0]) > 0:
  st.metric("Number of times you left a comment on a song without voting", df['times'])
  longest_comment = df['longest_comment'][0]
  st.caption(f"The longest comment you left was: \"{longest_comment}\"")