import streamlit as st
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

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

st.subheader("Song popularity")

query = """
select CONCAT(s."Artist(s)", ' - ', s.Title) as song, SUM(v."Points Assigned")::INTEGER as points
from competitors c
join submissions s on c.ID = s."Submitter ID"
join votes v on s."Spotify URI" = v."Spotify URI"
GROUP BY song
order by points desc;
"""

df = con.execute(query).df()
st.table(df)

st.subheader("Artist popularity")

query = """
select s."Artist(s)" as artist, COUNT(s."Artist(s)")::INTEGER as picked
from competitors c
join submissions s on c.ID = s."Submitter ID"
GROUP BY artist
order by picked desc;
"""

df = con.execute(query).df()
st.table(df)

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
sns.heatmap(normalized_matrix, annot=points_matrix.values, fmt='g', cmap="crest")
plt.title('Points distribution')
plt.xlabel('Points')
plt.ylabel('Name')

st.pyplot(plt)

st.subheader("Vote breakdown heatmap")

query = """
  select c.Name as voter, cs.Name as submitter, v."Points Assigned" as points
  from competitors c
  join votes v on c.ID = v."Voter ID"
  join submissions s on s."Spotify URI" = v."Spotify URI"  
  join competitors cs on cs.ID = s."Submitter ID"
  GROUP BY voter, submitter, points
"""

df = con.execute(query).df()

points_matrix = df.pivot_table(index='voter', columns='submitter', values='points', aggfunc='sum', fill_value=0)
plt.figure(figsize=(20, 12))
sns.heatmap(points_matrix, annot=True, cmap='coolwarm')
plt.title('Points Assigned by Competitors')
plt.xlabel('Submitter Name')
plt.ylabel('Voter Name')

st.pyplot(plt)

st.subheader("Vote comments wordcloud")

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

st.subheader("Submission comments wordcloud")

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