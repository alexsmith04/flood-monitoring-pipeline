import psycopg2
from config.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS readings (
    measure_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value DOUBLE PRECISION,
    PRIMARY KEY (measure_id, timestamp)
);
"""

def main():
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_QUERY)
        conn.commit()
        print("setup success")
    except Exception as e:
        print("setup error:", e)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()