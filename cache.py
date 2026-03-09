import redis
import json
import os
from config.config import REDIS_URL
from logger import get_logger

logger = get_logger(__name__)

CACHE_TTL = 3600
STATIONS_CACHE_KEY = 'stations:active'

client = redis.Redis.from_url(REDIS_URL)

def get_cached_stations():

    try:
        data = client.get(STATIONS_CACHE_KEY)
        if data:
            logger.info('Stations available in REDIS - loading from REDIS')
            return json.loads(data)
        logger.info('fetch stations from API')
        return None
    except redis.RedisError as e:
        logger.warning(f'Redis error, falling back to API: {e}')
        return None

def cache_stations(stations):

    try:
        client.setex(STATIONS_CACHE_KEY, CACHE_TTL, json.dumps(stations))
        logger.info(f'Cached {len(stations)} stations for {CACHE_TTL} seconds')
    except redis.RedisError as e:
        logger.warning(f'Failed to cache stations: {e}')