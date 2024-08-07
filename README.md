route:

Find nearest Septa Station: /nearest_station
header: {
        Content-Type
        my-api-key
    }
body:
    {
        longitude
        latitude
    }

Find nearest Metro Station: /nearest_metro
header: {
        Content-Type
        my-api-key
    }
body:
    {
        longitude
        latitude
    }

Find path: /directions
header: {
        Content-Type
        my-api-key
    }
body:
    {
        origin_longitude
        origin_latitude
        dest_longitude
        dest_latitude
    }