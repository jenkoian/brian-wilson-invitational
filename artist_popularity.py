import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Artist popularity (top 50)")

query = """
select s."Artist(s)" as artist, COUNT(s."Artist(s)")::INTEGER as picked
from competitors c
join submissions s on c.ID = s."Submitter ID"
GROUP BY artist
order by picked desc
LIMIT 50;
"""

df = con.execute(query).df()
df.index += 1
st.table(df)