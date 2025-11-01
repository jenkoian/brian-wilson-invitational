import streamlit as st
import duckdb
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Leaderboard")

query = """
select Name, SUM(v."Points Assigned")::INTEGER as points
from competitors c
join submissions s on c.ID = s."Submitter ID"
join votes v on s."Spotify URI" = v."Spotify URI"
GROUP BY Name
order by points desc;
"""
df = con.execute(query).df()
df.index += 1
st.table(df)