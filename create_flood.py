import os
import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=os.environ.get("DB_PORT", 5432),
)

conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE DATABASE flood;")
print("Database 'flood' created.")
cur.close()
conn.close()