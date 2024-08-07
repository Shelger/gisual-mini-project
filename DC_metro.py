import json
import pandas as pd
from geopy.distance import geodesic

def parse_geojson(filename):
    key_info_list = []
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for feature in data['features']:
        properties = feature['properties']
        geometry = feature['geometry']
        
        name = properties.get('NAME', 'N/A')
        address = properties.get('ADDRESS', 'N/A')
        coordinates = geometry.get('coordinates', [None, None])
        
        key_info = {
            'name': name,
            'address': address,
            'type': geometry.get('type', 'N/A'),
            'coordinates': {
                'longitude': coordinates[0],
                'latitude': coordinates[1]
            }
        }
        
        key_info_list.append(key_info)
    return pd.DataFrame(key_info_list)

def find_nearest_station(location, stations):
    min_distance = float('inf')
    nearest_station = None
    
    for _, station in stations.iterrows():
        station_location = (station['coordinates']['latitude'], station['coordinates']['longitude'])
        distance = geodesic(location, station_location).miles
        
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    
    return nearest_station

def station_to_geojson(station):
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [station['coordinates']['longitude'], station['coordinates']['latitude']]
        },
        "properties": {
            "name": station['name'],
            "address": station['address']
        }
    }
    return geojson
# stations = parse_geojson('Metro_Stations_Regional.geojson')
# location = (-76, 35)
# station = find_nearest_station(location, stations)
# print(station_to_geojson(station))