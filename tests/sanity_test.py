import psycopg2

conn = psycopg2.connect(
    host='flood.c3imyso0k5sr.eu-north-1.rds.amazonaws.com',
    port=5432,
    dbname='flood',
    user='postgres',
    password='password'
)

cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM public.readings;')
count = cur.fetchone()[0]
print(f'Total rows: {count}')

cur.close()
conn.close()