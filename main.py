import requests
import datetime
import time
from database import get_connection, insert_reading

ROOT = 'https://environment.data.gov.uk/flood-monitoring'
ALL_STATIONS = '/id/stations'

MAX_RETIRES = 3
RETRY_DELAY = 2

def get_dates():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)
    
    return start_date, end_date


def get_stations(status='Active'):

    params = {'status': status}

    r = requests.get(f'{ROOT}{ALL_STATIONS}', params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    stations = data.get('items', [])

    return stations


def get_station_ids(stations):

    station_ids = []

    for station in stations:
        station_ids.append(station['stationReference'])

    return station_ids


def fetch_readings_for_station(station_id, start_date, end_date):

    params = {'startdate': start_date, 'enddate': end_date, '_limit': 10000}

    for attempt in range(MAX_RETIRES):
        try:
            r = requests.get(f'{ROOT}/id/stations/{station_id}/readings', params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            return data.get('items', [])
        except requests.RequestException as e:
            print(f"attempt {attempt} failed for station {station_id}: {e}")

            if attempt < MAX_RETIRES - 1:
                print(f"retrying in {RETRY_DELAY} seconds")
                time.sleep(RETRY_DELAY)
            else:
                print(f"skipping station {station_id}, MAX RETRIES exceeded")
                return []

def transform_readings(raw_data):

    transformed = []
    for item in raw_data:
        if item.get('dateTime') and item.get('value') is not None:
            transformed.append({'measure_id': item['measure'],'timestamp': item['dateTime'],'value': item['value']})

    return transformed


if __name__ == '__main__':

    start_date, end_date = get_dates()
    stations = get_stations()
    station_ids = get_station_ids(stations)
    conn = get_connection()

    for station_id in station_ids:
        raw_data = fetch_readings_for_station(station_id, start_date, end_date)
        if not raw_data:
            continue

        transformed_data = transform_readings(raw_data)

        for reading in transformed_data:
            insert_reading(conn, reading['measure_id'], reading['timestamp'], reading['value'])
        
        conn.commit()
        print(f'Inserted {len(transformed_data)} readings for station {station_id}')

    conn.close()
    print('Inserted readings for active stations')