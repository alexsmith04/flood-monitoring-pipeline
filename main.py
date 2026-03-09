from utils import get_dates
from etl_pipeline.extract import fetch_stations
from etl_pipeline.transform import get_station_ids
from tasks import process_station
from logger import get_logger

logger = get_logger(__name__)

if __name__ == '__main__':
    start_date, end_date = get_dates()
    stations = fetch_stations()
    station_ids = get_station_ids(stations)

    for station_id in station_ids:
        process_station.delay(station_id, str(start_date), str(end_date))
        logger.info(f"Queued station {station_id}")

    logger.info(f"All {len(station_ids)} stations queued")