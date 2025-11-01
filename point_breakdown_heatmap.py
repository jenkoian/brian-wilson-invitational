import streamlit as st
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Point breakdown heatmap")

query = """
with unique_points as (
  select v."Points Assigned" as points
  from competitors c
  join votes v on c.ID = v."Voter ID"
  where v."Points Assigned" > 0
  GROUP BY points
  order by points desc
)
SELECT name as name, up.points::INTEGER as points, COUNT(up.points)::INTEGER as cnt
from competitors c
join votes v on c.ID = v."Voter ID"
join unique_points up on v."Points Assigned" = up.points
group by name, points
"""

df = con.execute(query).df()

points_matrix = df.pivot_table(index='name', columns='points', values='cnt', aggfunc='sum', fill_value=0)

# Normalize each column independently (0 to 1 scale per column)
normalized_matrix = points_matrix.apply(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else x, axis=0)

plt.figure(figsize=(20, 12))
sns.heatmap(normalized_matrix, annot=points_matrix.values, fmt='g', cmap='viridis')
plt.title('Points distribution')
plt.xlabel('Points')
plt.ylabel('Name')

st.pyplot(plt)