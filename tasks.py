from celery import Celery
from etl_pipeline.extract import fetch_readings_for_station
from etl_pipeline.transform import transform_readings
from etl_pipeline.load.connection import get_connection
from etl_pipeline.load.load import insert_reading
from config.config import RABBITMQ_URL, REDIS_URL
from logger import get_logger

logger = get_logger(__name__)

app = Celery(
    'flood_etl',
    broker=RABBITMQ_URL,
    backend=REDIS_URL
)

@app.task(bind=True, max_retries=3, default_retry_delay=2)
def process_station(self, station_id, start_date, end_date):
    logger.info(f"Processing station {station_id}")

    try:
        raw_data = fetch_readings_for_station(station_id, start_date, end_date)
    except Exception as exc:
        raise self.retry(exc=exc)

    if not raw_data:
        logger.warning(f"No data for station {station_id}")
        return f'No data for {station_id}'

    readings = transform_readings(raw_data)

    conn = get_connection()
    for reading in readings:
        insert_reading(conn, reading['measure_id'], reading['timestamp'], reading['value'])
    conn.commit()
    conn.close()

    logger.info(f"Inserted {len(readings)} readings for station {station_id}")
    return f'Inserted {len(readings)} readings for {station_id}'