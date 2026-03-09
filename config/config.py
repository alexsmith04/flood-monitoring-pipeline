import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

REDIS_URL = os.getenv("REDIS_URL")

ROOT = 'https://environment.data.gov.uk/flood-monitoring'
ALL_STATIONS = '/id/stations'
MAX_RETIRES = 3
RETRY_DELAY = 2