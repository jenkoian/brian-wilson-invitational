import zipfile
import duckdb

print('Unzipping export.zip...')
with zipfile.ZipFile('export.zip', 'r') as zip_ref:
    zip_ref.extractall('data/')
    zip_ref.close()


print('Building database...')
con = duckdb.connect(database='bwi.duckdb')

for file in ['competitors.csv', 'rounds.csv', 'submissions.csv', 'votes.csv']:
    query = f"CREATE OR REPLACE TABLE {file.replace('.csv', '')} AS SELECT * FROM read_csv('data/{file}')"
    con.execute(query)