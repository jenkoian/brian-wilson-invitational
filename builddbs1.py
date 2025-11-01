import zipfile
import duckdb

print('Unzipping season1.zip...')
with zipfile.ZipFile('season1.zip', 'r') as zip_ref:
    zip_ref.extractall('season1/')
    zip_ref.close()


print('Building database...')
con = duckdb.connect(database='season1.duckdb')

for file in ['competitors.csv', 'rounds.csv', 'submissions.csv', 'votes.csv']:
    query = f"CREATE OR REPLACE TABLE {file.replace('.csv', '')} AS SELECT * FROM read_csv('season1/{file}')"
    con.execute(query)