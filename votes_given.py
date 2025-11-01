import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Votes given")

query = """
select Name
from competitors
order by Name asc
"""
competitors = con.execute(query).df()

with st.container(border=True):
    voter = st.selectbox("Voter", competitors['Name'], index=None, placeholder="Select voter...")
    submitter = st.selectbox("Submitter", competitors['Name'], index=None, placeholder="Select submitter...")

query = """
SELECT cv.Name as Voter, cs.Name as Submitter, r."name" as Round, 
CONCAT(s."Artist(s)", ' - ', s.title) as Song,
v."Points Assigned"::INTEGER as "Points Awarded",
v."Comment" as Comment
FROM rounds r
JOIN submissions s on r.ID = s."Round ID"
JOIN competitors cs ON s."Submitter ID" = cs.ID
JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
JOIN competitors cv ON v."Voter ID" = cv.ID
WHERE voter = ?
AND submitter = ?
"""

df = con.execute(query, (voter, submitter)).df()
df.index += 1
st.table(df)