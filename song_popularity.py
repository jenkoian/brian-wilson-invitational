import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Song popularity (top 50)")

query = """
select CONCAT(s."Artist(s)", ' - ', s.Title) as song, LISTAGG(DISTINCT c.Name, ', ') as name, SUM(v."Points Assigned")::INTEGER as points
from competitors c
join submissions s on c.ID = s."Submitter ID"
join votes v on s."Spotify URI" = v."Spotify URI"
GROUP BY song
order by points desc
LIMIT 50;
"""

df = con.execute(query).df()
df.index += 1
st.table(df)