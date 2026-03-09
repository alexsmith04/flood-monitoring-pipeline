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