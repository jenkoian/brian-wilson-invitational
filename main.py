import streamlit as st
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd

con = duckdb.connect(database='bwi.duckdb')

st.title("🎵Brian Wilson Invitational Stats")

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
st.table(df)

st.subheader("Song popularity (top 50)")

query = """
select CONCAT(s."Artist(s)", ' - ', s.Title) as song, SUM(v."Points Assigned")::INTEGER as points
from competitors c
join submissions s on c.ID = s."Submitter ID"
join votes v on s."Spotify URI" = v."Spotify URI"
GROUP BY song
order by points desc
LIMIT 50;
"""

df = con.execute(query).df()
st.table(df)

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
st.table(df)

# st.subheader("Vote breakdown by point")
#
# query = """
# with unique_points as (
#   select v."Points Assigned" as points
#   from competitors c
#   join votes v on c.ID = v."Voter ID"
#   GROUP BY points
#   order by points desc
# )
# SELECT name, up.points::INTEGER as points, COUNT(up.points)::INTEGER as cnt
# from competitors c
# join votes v on c.ID = v."Voter ID"
# join unique_points up on v."Points Assigned" = up.points
# group by name, points
# order by points desc, cnt desc, name asc;
# """
#
# df = con.execute(query).df()
# st.table(df)

st.subheader("Season 3 point breakdown heatmap")

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
sns.heatmap(normalized_matrix, annot=points_matrix.values, fmt='g', cmap="crest")
plt.title('Season 3 points distribution')
plt.xlabel('Points')
plt.ylabel('Name')

st.pyplot(plt)

st.subheader("Season 3 vote breakdown heatmap")

query = """
SELECT cv.Name as voter, cs.Name as submitter, v."Points Assigned"::INTEGER as points
FROM rounds r
JOIN submissions s on r.ID = s."Round ID"
JOIN competitors cs ON s."Submitter ID" = cs.ID
JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
JOIN competitors cv ON v."Voter ID" = cv.ID
GROUP BY voter, submitter, r.ID, points
"""

df = con.execute(query).df()

points_matrix = df.pivot_table(index='voter', columns='submitter', values='points', aggfunc='sum', fill_value=0)

#st.table(points_matrix)

plt.figure(figsize=(20, 12))
sns.heatmap(points_matrix, annot=True, cmap='coolwarm', fmt='g')
plt.title('Season 3 points Assigned by Competitors')
plt.xlabel('Submitter Name')
plt.ylabel('Voter Name')

st.pyplot(plt)

st.subheader("Season 3 vote comments wordcloud")

query = """
WITH words AS (
    SELECT 
        UNNEST(REGEXP_SPLIT_TO_ARRAY(Comment, ' ')) AS word
    FROM votes
)
SELECT STRING_AGG(word, ',') AS final_string
FROM words;  
"""

comments = con.execute(query).fetchone()

# Filter out 'song' as too common
filtered = ','.join([item for item in comments[0].split(',') if item.lower() != 'song'])

wordcloud = WordCloud(width=1600, height=800).generate(filtered)

fig, ax = plt.subplots(figsize=(20, 10), facecolor='k')
ax.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.tight_layout(pad=0)
st.pyplot(fig)

st.subheader("Season 3 submission comments wordcloud")

query = """
WITH words AS (
    SELECT 
        UNNEST(REGEXP_SPLIT_TO_ARRAY(Comment, ' ')) AS word
    FROM submissions
)
SELECT STRING_AGG(word, ',') AS final_string
FROM words;    
"""

comments = con.execute(query).fetchone()

# Filter out 'song' as too common
filtered = ','.join([item for item in comments[0].split(',') if item.lower() != 'song'])

wordcloud = WordCloud(width=1600, height=800).generate(filtered)

fig, ax = plt.subplots(figsize=(20, 10), facecolor='k')
ax.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.tight_layout(pad=0)
st.pyplot(fig)

st.subheader("Season 3 voting by playlist position")

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

# st.subheader("Cross season voting by playlist position")
#
# s1_con = duckdb.connect(database='season1.duckdb')
# s2_con = duckdb.connect(database='season2.duckdb')
#
# s1_query = """
# with song_positions as (
#   SELECT r.Name as round, CONCAT(s."Artist(s)", ' ', s."Title") as song,
#   ROW_NUMBER() OVER(PARTITION BY r.Name ORDER BY s."Spotify URI" asc) as position,
#   SUM(v."Points Assigned") as votes
#   FROM submissions s
#   JOIN rounds r ON r.ID = s."Round ID"
#   JOIN votes v ON s."Spotify URI" = v."Spotify URI"
#   GROUP BY round, song, s."Spotify URI"
#   ORDER BY votes DESC
# )
# select position, SUM(votes) as votes
# from song_positions
# group by position
# order by votes desc;
# """
#
# s1_df = s1_con.execute(s1_query).df()
#
# s2_query = """
# with song_positions as (
#   SELECT r.Name as round, CONCAT(s."Artist(s)", ' ', s."Title") as song,
#   ROW_NUMBER() OVER(PARTITION BY r.Name ORDER BY s."Spotify URI" asc) as position,
#   SUM(v."Points Assigned") as votes
#   FROM submissions s
#   JOIN rounds r ON r.ID = s."Round ID"
#   JOIN votes v ON s."Spotify URI" = v."Spotify URI"
#   GROUP BY round, song, s."Spotify URI"
#   ORDER BY votes DESC
# )
# select position, SUM(votes) as votes
# from song_positions
# group by position
# order by votes desc;
# """
#
# s2_df = s2_con.execute(s2_query).df()
#
# s3_query = """
# with song_positions as (
#   SELECT r.Name as round, CONCAT(s."Artist(s)", ' ', s."Title") as song,
#   ROW_NUMBER() OVER(PARTITION BY r.Name ORDER BY s."Spotify URI" asc) as position,
#   SUM(v."Points Assigned") as votes
#   FROM submissions s
#   JOIN rounds r ON r.ID = s."Round ID"
#   JOIN votes v ON s."Spotify URI" = v."Spotify URI"
#   GROUP BY round, song, s."Spotify URI"
#   ORDER BY votes DESC
# )
# select position, SUM(votes) as votes
# from song_positions
# group by position
# order by votes desc;
# """
#
# s3_df = con.execute(s3_query).df()
#
# s1_df.insert(0, "season", 1, allow_duplicates=True)
# s2_df.insert(0, "season", 2, allow_duplicates=True)
# s3_df.insert(0, "season", 3, allow_duplicates=True)
#
# df = pd.concat([s1_df, s2_df, s3_df], ignore_index=True)
#
# plt.figure(figsize=(10, 12))
# sns.lmplot(x='position', y='votes', data=df, hue='season')
# st.pyplot(plt)