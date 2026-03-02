import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        port=os.environ.get('DB_PORT', 5432)
    )

def insert_reading(conn, measure_id, timestamp, value):
    with conn.cursor() as cur:
        cur.execute(
            '''
            INSERT INTO readings (measure_id, timestamp, value)
            VALUES (%s, %s, %s)
            ON CONFLICT (measure_id, timestamp) DO NOTHING
            ''',
            (measure_id, timestamp, value)
        )
