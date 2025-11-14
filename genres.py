import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Submitter genres")

query = """
SELECT
    c.Name AS submitter,
    list_distinct(flatten(LIST(s.genres))) AS all_unique_genres
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