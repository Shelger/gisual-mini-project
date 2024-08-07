from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import septa
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import DC_metro
from mangum import Mangum

load_dotenv()
kmz_file_path = 'SEPTARegionalRailStations2016.kmz'
metro_file_path = 'Metro_Stations_Regional.geojson'
api_key = os.getenv('GOOGLE_MAP_API_KEY')
app = Flask(__name__)
# 1. caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# 2. Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "10 per hour"]
)
# 3. Auto-scaling

my_api_key = os.getenv('MY_API_KEY')
# Only let the area of PA access to this api, in case the worldwide user cost too much on Google Map API
SERVICEABLE_AREA = {
    'min_latitude': 39.0,
    'max_latitude': 41.0,
    'min_longitude': -76.0,
    'max_longitude': -74.0
}
def is_within_serviceable_area(latitude, longitude):
    return (SERVICEABLE_AREA['min_latitude'] <= latitude <= SERVICEABLE_AREA['max_latitude'] and
            SERVICEABLE_AREA['min_longitude'] <= longitude <= SERVICEABLE_AREA['max_longitude'])


def check_api_key(request):
    api_key = request.headers.get('my-api-key')
    print(api_key)
    return api_key == my_api_key

@app.before_request
def before_request_func():
    if not check_api_key(request):
        return jsonify({'error': 'Unauthorized'}), 401

# I will use load balancer
@app.route('/nearest_station', methods=['POST'])
@limiter.limit("10 per minute")
@cache.cached(timeout=300, query_string=True)
def nearest_station():
    try:
        data = request.get_json()
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (TypeError, ValueError, KeyError):
        return jsonify({'error': 'Invalid latitude or longitude'}), 400
    
    if not is_within_serviceable_area(latitude, longitude):
        return jsonify({'error': 'Out of range', 'message': 'You are not in the serviceable area'}), 400

    location = (latitude, longitude)
    kml_content = septa.extract_kml_from_kmz(kmz_file_path)
    stations = septa.parse_kml(kml_content)
    nearest_station = septa.find_nearest_station(location, stations)
    station_geojson = septa.station_to_geojson(nearest_station)
    
    return jsonify(station_geojson)


@app.route('/directions', methods=['POST'])
@limiter.limit("10 per minute")
@cache.cached(timeout=300, query_string=True)
def directions():
    try:
        data = request.get_json()
        origin_latitude = float(data['origin_latitude'])
        origin_longitude = float(data['origin_longitude'])
        dest_latitude = float(data['dest_latitude'])
        dest_longitude = float(data['dest_longitude'])
    except (TypeError, ValueError, KeyError):
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    origin = (origin_latitude, origin_longitude)
    destination = (dest_latitude, dest_longitude)
    
    directions = septa.get_walking_directions(api_key, origin, destination)
    
    return jsonify(directions)

@app.route('/nearest_metro', methods=['POST'])
@limiter.limit("10 per minute")
@cache.cached(timeout=300, query_string=True)
def nearest_metro():
    try:
        data = request.get_json()
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
    except (TypeError, ValueError, KeyError):
        return jsonify({'error': 'Invalid latitude or longitude'}), 400
    
    stations = DC_metro.parse_geojson(metro_file_path)
    location = (longitude, latitude)
    nearest_metro_station = DC_metro.find_nearest_station(location, stations)
    return DC_metro.station_to_geojson(nearest_metro_station)

lambda_handler = Mangum(app)

if __name__ == '__main__':
    app.run(debug=True)