import streamlit as st
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Voting by playlist position")

query = """
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

df = con.execute(query).df()
plt.figure(figsize=(10, 12))
sns.lmplot(x='position', y='votes', data=df)
st.pyplot(plt)