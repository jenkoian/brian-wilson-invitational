import streamlit as st
import duckdb

con = duckdb.connect(database='bwi.duckdb')

query = """
with round_songs as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' - ', s.title) as song, 
  s."Spotify URI" as spotify_uri,
  SUM(v."Points Assigned") as score
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  GROUP BY round, song, spotify_uri
),
round_winning_songs as (
  select round, MAX_BY(song, score) as song, MAX_BY(spotify_uri, score) as spotify_uri
  from round_songs
  group by round
)
select COUNT(1) as times, SUM(v."Points Assigned") as votes
from round_winning_songs rws 
join votes v on rws.spotify_uri = v."Spotify URI"
join competitors c on v."Voter ID" = c.ID
where v."Points Assigned" > 0  
and c."name" = ?;
"""

df = con.execute(query, [competitor]).df()

st.metric("How often you (up)voted the winning song", df['times'])

if int(df['times'][0]) > 0:
  votes = int(df['votes'][0])
  votes_str = 'votes' if votes != 1 else 'vote'
  st.caption(f"You dished out {votes} {votes_str} to the winning songs in total")

query = """
with round_songs as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' - ', s.title) as song, 
  s."Spotify URI" as spotify_uri,
  SUM(v."Points Assigned") as score
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  GROUP BY round, song, spotify_uri
),
round_winning_songs as (
  select round, MAX_BY(song, score) as song, MAX_BY(spotify_uri, score) as spotify_uri
  from round_songs
  group by round
)
select COUNT(1) as times, SUM(v."Points Assigned") as votes
from round_winning_songs rws 
join votes v on rws.spotify_uri = v."Spotify URI"
join competitors c on v."Voter ID" = c.ID
where v."Points Assigned" < 0  
and c."name" = ?;
"""

df = con.execute(query, [competitor]).df()

st.metric("How often you (down)voted the winning song", df['times'])

if int(df['times'][0]) > 0:
  votes = int(df['votes'][0])
  votes_str = 'votes' if votes != 1 else 'vote'
  st.caption(f"You dished out {votes} {votes_str} to the winning songs in total")

query = """
with round_songs as (
  SELECT r.Name as round, CONCAT(s."Artist(s)", ' - ', s.title) as song, 
  s."Spotify URI" as spotify_uri,
  SUM(v."Points Assigned") as score
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  GROUP BY round, song, spotify_uri
),
round_losing_songs as (
  select round, MIN_BY(song, score) as song, MIN_BY(spotify_uri, score) as spotify_uri
  from round_songs
  group by round
)
select COUNT(1) as times, SUM(v."Points Assigned") as votes
from round_losing_songs rws 
join votes v on rws.spotify_uri = v."Spotify URI"
join competitors c on v."Voter ID" = c.ID
where v."Points Assigned" > 0  
and c."name" = ?;
"""

df = con.execute(query, [competitor]).df()

st.metric("How often you (up)voted the losing song", df['times'])

if int(df['times'][0]) > 0:
  votes = int(df['votes'][0])
  votes_str = 'votes' if votes != 1 else 'vote'
  st.caption(f"You dished out {votes} {votes_str} to the losing songs in total")

query = """
WITH comments_no_points as (
  SELECT cv.Name as voter, cs.Name as submitter, r."name" as round, 
  CONCAT(s."Artist(s)", ' - ', s.title) as song,
  v."Points Assigned"::INTEGER as points,
  v."Comment" as comment,
  LENGTH(v."Comment") as comment_length
  FROM rounds r
  JOIN submissions s on r.ID = s."Round ID"
  JOIN competitors cs ON s."Submitter ID" = cs.ID
  JOIN votes v ON v."Spotify URI" = s."Spotify URI" AND v."Round ID" = s."Round ID"
  JOIN competitors cv ON v."Voter ID" = cv.ID
  WHERE v."Comment" is not null
  AND points = 0
)
SELECT COUNT(1) as times, MAX_BY(comment, comment_length) as longest_comment
FROM comments_no_points
WHERE voter = ?;
"""

df = con.execute(query, [competitor]).df()

if int(df['times'][0]) > 0:
  st.metric("Number of times you left a comment on a song without voting", df['times'])
  longest_comment = df['longest_comment'][0]
  st.caption(f"The longest comment you left was: \"{longest_comment}\"")