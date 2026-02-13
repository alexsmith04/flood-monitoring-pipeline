import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='flood',
        user='postgres',
        password='password',
        port=5433
    )
    return conn

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
