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
        title=f"Submitted genres for **{competitor}**" if id_var == 'submitter' else f"Voted genres for {competitor}",
        template='plotly_white'
    )

    # Customize the layout
    fig.update_traces(fill='toself') # Fills the area inside the line

    return fig

st.subheader("Genre Radar Charts")

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
    st.plotly_chart(radar_fig, width='stretch')

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

st.subheader("Genre popularity (top 50)")

query = """
-- Most popular genre
with genres as (
  select unnest(flatten(LIST(s.spotify_genres || s.lastfm_genres))) as genre, CONCAT(s."Artist(s)", ' - ', s.Title) as song
  from competitors c
  join submissions s on c.ID = s."Submitter ID"
  join votes v on s."Spotify URI" = v."Spotify URI"
  group by CONCAT(s."Artist(s)", ' - ', s.Title)
)
select genre, first(song) as example_song, count(*) as picked
from genres
group by genre
order by picked desc
limit 50;
"""

df = con.execute(query).df()
df.index += 1
st.table(df)

st.subheader("Genre unpopularity (bottom 50)")

query = """
-- Most popular genre
with genres as (
  select unnest(flatten(LIST(s.spotify_genres || s.lastfm_genres))) as genre, CONCAT(s."Artist(s)", ' - ', s.Title) as song
  from competitors c
  join submissions s on c.ID = s."Submitter ID"
  join votes v on s."Spotify URI" = v."Spotify URI"
  group by CONCAT(s."Artist(s)", ' - ', s.Title)
)
select genre, first(song) as example_song, count(*) as picked
from genres
group by genre
order by picked asc
limit 50;
"""

df = con.execute(query).df()
df.index += 1
st.table(df)

st.subheader("Submitter genres")

query = """
SELECT
    c.Name AS submitter,
    list_distinct(flatten(LIST(s.spotify_genres || s.lastfm_genres))) AS all_unique_genres
FROM
    submissions s
JOIN
    competitors c ON s."Submitter ID" = c.ID
GROUP BY
    c.Name;
"""

df = con.execute(query).df()
df.index += 1
st.table(df)