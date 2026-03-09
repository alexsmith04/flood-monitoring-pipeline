def get_station_ids(stations):

    station_ids = []
    for station in stations:
        station_ids.append(station['stationReference'])

    return station_ids

def transform_readings(raw_data):

    transformed = []
    for item in raw_data:
        if item.get('dateTime') and item.get('value') is not None:
            transformed.append({'measure_id': item['measure'],'timestamp': item['dateTime'],'value': item['value']})

    return transformed