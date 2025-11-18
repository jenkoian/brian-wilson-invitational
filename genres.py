import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Genre popularity (top 50)")

query = """
-- Most popular genre
with genres as (
  select unnest(flatten(LIST(s.spotify_genres || s.lastfm_genres))) as genre
  from competitors c
  join submissions s on c.ID = s."Submitter ID"
  join votes v on s."Spotify URI" = v."Spotify URI"
)
select genre, count(*) as picked
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
  select unnest(flatten(LIST(s.spotify_genres || s.lastfm_genres))) as genre
  from competitors c
  join submissions s on c.ID = s."Submitter ID"
  join votes v on s."Spotify URI" = v."Spotify URI"
)
select genre, count(*) as picked
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