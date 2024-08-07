import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from geopy.distance import geodesic
import json
import requests
from dotenv import load_dotenv
import os

def extract_kml_from_kmz(kmz_file_path):
    with zipfile.ZipFile(kmz_file_path, 'r') as kmz:
        for file_name in kmz.namelist():
            if file_name.endswith('.kml'):
                with kmz.open(file_name, 'r') as kml_file:
                    return kml_file.read()

def parse_kml(kml_content):
    root = ET.fromstring(kml_content)
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    stations = []
    
    for placemark in root.findall('.//kml:Placemark', namespace):
        name = placemark.find('kml:name', namespace).text
        coordinates = placemark.find('.//kml:coordinates', namespace).text
        longitude, latitude, _ = map(float, coordinates.strip().split(','))
        
        stations.append({
            'station_name': name,
            'latitude': latitude,
            'longitude': longitude
        })
    
    return pd.DataFrame(stations)

def find_nearest_station(location, stations):
    min_distance = float('inf')
    nearest_station = None
    
    for _, station in stations.iterrows():
        station_location = (station['latitude'], station['longitude'])
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
            "coordinates": [station['longitude'], station['latitude']]
        },
        "properties": {
            "name": station['station_name']
        }
    }
    return geojson

def get_walking_directions(api_key, origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin[0]},{origin[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "mode": "walking",
        "key": api_key
    }
    response = requests.get(url, params=params)
    return response.json()

def get_nearest_station(location, kmz_file_path, api_key):
    kml_content = extract_kml_from_kmz(kmz_file_path)
    stations = parse_kml(kml_content)
    nearest_station = find_nearest_station(location, stations)
    station_geojson = station_to_geojson(nearest_station)
    return station_geojson


# location = (-75,39)
# kmz_file_path = '/Users/shelger/2024/Gisual/SEPTARegionalRailStations2016.kmz'
# load_dotenv()
# api_key = os.getenv('GOOGLE_MAP_API_KEY')
# geojson, directions = get_nearest_station_with_directions(location, kmz_file_path, api_key)

# print("GeoJSON:", json.dumps(geojson, indent=2))
# print("Directions:", json.dumps(directions, indent=2))