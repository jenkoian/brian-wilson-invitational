import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Vote breakdown by point")

query = """
with unique_points as (
  select v."Points Assigned" as points
  from competitors c
  join votes v on c.ID = v."Voter ID"
  GROUP BY points
  order by points desc
)
SELECT name, up.points::INTEGER as points, COUNT(up.points)::INTEGER as cnt
from competitors c
join votes v on c.ID = v."Voter ID"
join unique_points up on v."Points Assigned" = up.points
group by name, points
order by points desc, cnt desc, name asc;
"""

df = con.execute(query).df()
st.table(df)