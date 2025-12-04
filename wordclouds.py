import streamlit as st
import duckdb
import matplotlib.pyplot as plt
from wordcloud import WordCloud

con = duckdb.connect(database='bwi.duckdb')

st.subheader("Vote comments wordcloud")

query = """
WITH words AS (
    SELECT 
        UNNEST(
          REGEXP_SPLIT_TO_ARRAY(
            regexp_replace(Comment,'[^a-zA-Z0-9\s]', ' ', 'g'), 
            ' '
          )
        ) AS word
    FROM votes
    WHERE char_length(Comment) > 2
)
SELECT STRING_AGG(DISTINCT word, ',') AS final_string
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
        UNNEST(
          REGEXP_SPLIT_TO_ARRAY(
            regexp_replace(Comment,'[^a-zA-Z0-9\s]', ' ', 'g'), 
            ' '
          )
        ) AS word
    FROM submissions
    WHERE char_length(Comment) > 2
)
SELECT STRING_AGG(DISTINCT word, ',') AS final_string
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
