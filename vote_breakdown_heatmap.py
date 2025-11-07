import streamlit as st
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Vote breakdown heatmap")

query = """
select c.Name as voter, cs.Name as submitter,
SUM(v."Points Assigned"::INTEGER) as points
from competitors c
join votes v on c.ID = v."Voter ID"
join submissions s on s."Spotify URI" = v."Spotify URI"  
join rounds r on s."Round ID" = r.ID and v."Round ID" = r.ID
join competitors cs on cs.ID = s."Submitter ID"
GROUP BY voter, submitter, r.id
"""

df = con.execute(query).df()

points_matrix = df.pivot_table(index='voter', columns='submitter', values='points', aggfunc='sum', fill_value=0)

#st.table(points_matrix)

plt.figure(figsize=(20, 12))
sns.heatmap(points_matrix, annot=True, cmap='viridis', fmt='g')
plt.title('Points Assigned by Competitors')
plt.xlabel('Submitter Name')
plt.ylabel('Voter Name')

st.pyplot(plt)
