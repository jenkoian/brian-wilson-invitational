import zipfile
import duckdb

print('Unzipping season2.zip...')
with zipfile.ZipFile('season2.zip', 'r') as zip_ref:
    zip_ref.extractall('season2/')
    zip_ref.close()


print('Building database...')
con = duckdb.connect(database='season2.duckdb')

for file in ['competitors.csv', 'rounds.csv', 'submissions.csv', 'votes.csv']:
    query = f"CREATE OR REPLACE TABLE {file.replace('.csv', '')} AS SELECT * FROM read_csv('season2/{file}')"
    con.execute(query)