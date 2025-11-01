import streamlit as st
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Cross season voting by playlist position")

s1_con = duckdb.connect(database='season1.duckdb')
s2_con = duckdb.connect(database='season2.duckdb')

s1_query = """
with song_positions as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' ', s."Title") as song,
  ROW_NUMBER() OVER(PARTITION BY r.Name ORDER BY s."Spotify URI" asc) as position,
  SUM(v."Points Assigned") as votes
  FROM submissions s
  JOIN rounds r ON r.ID = s."Round ID"
  JOIN votes v ON s."Spotify URI" = v."Spotify URI"
  GROUP BY round, song, s."Spotify URI"
  ORDER BY votes DESC
)
select position, SUM(votes) as votes
from song_positions
group by position
order by votes desc;
"""

s1_df = s1_con.execute(s1_query).df()

s2_query = """
with song_positions as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' ', s."Title") as song,
  ROW_NUMBER() OVER(PARTITION BY r.Name ORDER BY s."Spotify URI" asc) as position,
  SUM(v."Points Assigned") as votes
  FROM submissions s
  JOIN rounds r ON r.ID = s."Round ID"
  JOIN votes v ON s."Spotify URI" = v."Spotify URI"
  GROUP BY round, song, s."Spotify URI"
  ORDER BY votes DESC
)
select position, SUM(votes) as votes
from song_positions
group by position
order by votes desc;
"""

s2_df = s2_con.execute(s2_query).df()

s3_query = """
with song_positions as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' ', s."Title") as song,
  ROW_NUMBER() OVER(PARTITION BY r.Name ORDER BY s."Spotify URI" asc) as position,
  SUM(v."Points Assigned") as votes
  FROM submissions s
  JOIN rounds r ON r.ID = s."Round ID"
  JOIN votes v ON s."Spotify URI" = v."Spotify URI"
  GROUP BY round, song, s."Spotify URI"
  ORDER BY votes DESC
)
select position, SUM(votes) as votes
from song_positions
group by position
order by votes desc;
"""

s3_df = con.execute(s3_query).df()

s1_df.insert(0, "season", 1, allow_duplicates=True)
s2_df.insert(0, "season", 2, allow_duplicates=True)
s3_df.insert(0, "season", 3, allow_duplicates=True)

df = pd.concat([s1_df, s2_df, s3_df], ignore_index=True)

plt.figure(figsize=(10, 12))
sns.lmplot(x='position', y='votes', data=df, hue='season')
st.pyplot(plt)
