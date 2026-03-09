import requests
import time

from config.config import ROOT, ALL_STATIONS, MAX_RETIRES, RETRY_DELAY
from logger import get_logger

logger = get_logger(__name__)

def fetch_stations(status='Active'):
    params = {'status': status}
    r = requests.get(f'{ROOT}{ALL_STATIONS}', params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    stations = data.get('items', [])
    return stations

def fetch_readings_for_station(station_id, start_date, end_date):
    params = {'startdate': start_date, 'enddate': end_date, '_limit': 10000}

    for attempt in range(MAX_RETIRES):
        try:
            r = requests.get(f'{ROOT}/id/stations/{station_id}/readings', params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            return data.get('items', [])
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for station {station_id}: {e}")

            if attempt < MAX_RETIRES - 1:
                logger.warning(f"Retrying in {RETRY_DELAY} seconds")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Skipping station {station_id} — max retries exceeded")
                return []