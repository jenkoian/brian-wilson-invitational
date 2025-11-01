import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Songs evoking 0 votes either way")

query = """
select CONCAT(s."Artist(s)", ' - ', s.Title) as song, C.Name as name, r.Name as round
from competitors c
join submissions s on c.ID = s."Submitter ID"
join rounds r on s."Round ID" = r.ID
left join votes v on s."Spotify URI" = v."Spotify URI"
where v."Points Assigned" is null
LIMIT 50;
"""

df = con.execute(query).df()
df.index += 1
st.table(df)