from geopy.geocoders import Nominatim

async def get_coordinates(location):
    geolocator = Nominatim(user_agent = 'geo_converter')
    location_query = f'{location}, Cardiff'

    location = geolocator.geocode(location_query)

    return {'latitude': location.latitude , 'longitude': location.longitude}