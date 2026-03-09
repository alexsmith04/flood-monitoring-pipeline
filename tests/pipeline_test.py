import unittest
import requests
from unittest.mock import patch

from etl_pipeline.transform import transform_readings, get_station_ids
from etl_pipeline.extract import fetch_readings_for_station
from etl_pipeline.load.connection import get_connection
from etl_pipeline.load.load import insert_reading


class TestTransformFunctions(unittest.TestCase):

    def test_transform_readings_filters_invalid_rows(self):
        raw_data = [
            {'measure': 'm1', 'dateTime': '2026-02-01T00:00:00Z', 'value': 1.23},
            {'measure': 'm2', 'dateTime': None, 'value': 2.34},
            {'measure': 'm3', 'dateTime': '2026-02-01T01:00:00Z', 'value': None},
        ]

        result = transform_readings(raw_data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['measure_id'], 'm1')
        self.assertEqual(result[0]['value'], 1.23)

    def test_transform_readings_empty_input(self):
        self.assertEqual(transform_readings([]), [])

    def test_get_station_ids_extracts_correctly(self):
        stations = [
            {'stationReference': 'A1'},
            {'stationReference': 'B2'},
            {'stationReference': 'C3'},
        ]
        result = get_station_ids(stations)
        self.assertEqual(result, ['A1', 'B2', 'C3'])

    def test_get_station_ids_empty_input(self):
        self.assertEqual(get_station_ids([]), [])


class TestFetchReadings(unittest.TestCase):

    @patch('etl_pipeline.extract.requests.get')
    def test_fetch_readings_max_retries_exceeded(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()

        result = fetch_readings_for_station('123', '2026-02-01', '2026-02-02')

        self.assertEqual(result, [])

class TestDatabaseIntegration(unittest.TestCase):

    def test_insert_idempotent(self):
        conn = get_connection()

        try:
            insert_reading(conn, 'test_measure', '2026-02-01 00:00:00', 1.23)
            insert_reading(conn, 'test_measure', '2026-02-01 00:00:00', 1.23)
            conn.commit()

            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM readings WHERE measure_id = 'test_measure'"
            )
            count = cur.fetchone()[0]

            self.assertEqual(count, 1)

            #cleanup
            cur.execute(
                "DELETE FROM readings WHERE measure_id = 'test_measure'"
            )
            conn.commit()
        finally:
            conn.close()


if __name__ == '__main__':
    unittest.main()