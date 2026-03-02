import datetime
from database import get_connection, insert_reading
from rate_limiter import RateLimiter
import aiohttp
import asyncio

ROOT = 'https://environment.data.gov.uk/flood-monitoring'
ALL_STATIONS = '/id/stations'

MAX_RETIRES = 3
RETRY_DELAY = 2
CONCURRENCY_LIMIT = 10
RATE_LIMIT = 6

def get_dates():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)
    
    return start_date.isoformat(), end_date.isoformat()


async def get_stations(session, status='Active'):

    params = {'status': status}

    async with session.get(f'{ROOT}{ALL_STATIONS}', params=params, timeout=60) as r:
        r.raise_for_status()
        data = await r.json()
        stations = data.get('items', [])

        return stations


def get_station_ids(stations):

    station_ids = []

    for station in stations:
        station_ids.append(station['stationReference'])

    return station_ids


async def fetch_readings_for_station(session, station_id, start_date, end_date, semaphore, rate_limiter):

    params = {'startdate': start_date, 'enddate': end_date, '_limit': 10000}

    async with semaphore:
        for attempt in range(MAX_RETIRES):
            try:
                await rate_limiter.wait()

                async with session.get(f'{ROOT}/id/stations/{station_id}/readings', params=params, timeout=60) as r:
                    r.raise_for_status()
                    data = await r.json()
                    return station_id, data.get('items', [])
                
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"attempt {attempt} failed for station {station_id}: {e}")

                if attempt < MAX_RETIRES - 1:
                    backoff = (2 ** attempt) + 0.5
                    print(f"retrying in {backoff} seconds")
                    await asyncio.sleep(backoff)
                else:
                    print(f"skipping station {station_id}, MAX RETRIES exceeded")
                    return station_id, []

def transform_readings(raw_data):

    transformed = []
    for item in raw_data:
        if item.get('dateTime') and item.get('value') is not None:
            transformed.append({'measure_id': item['measure'],'timestamp': item['dateTime'],'value': item['value']})

    return transformed

async def main():

    start_date, end_date = get_dates()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    rate_limiter = RateLimiter(RATE_LIMIT)

    async with aiohttp.ClientSession() as session:
        stations = await get_stations(session)
        station_ids = get_station_ids(stations)

        tasks = [fetch_readings_for_station(session, station_id, start_date, end_date, semaphore, rate_limiter) for station_id in station_ids]

        results = await asyncio.gather(*tasks)

    conn = get_connection()

    for station_id, raw_data in results:
        if not raw_data:
            continue

        transformed_data = transform_readings(raw_data)

        for reading in transformed_data:
            insert_reading(conn, reading['measure_id'], reading['timestamp'], reading['value'])
        
        conn.commit()
        print(f'Inserted {len(transformed_data)} readings for station {station_id}')

    conn.close()
    print('Inserted readings for active stations')

if __name__ == "__main__":
    asyncio.run(main())