from geopy.geocoders import Nominatim

async def get_coordinates(location):

    try:
        geolocator = Nominatim(user_agent = 'geo_converter')
        location_query = f'{location}, Cardiff'

        location = geolocator.geocode(location_query)

        return {'latitude': location.latitude , 'longitude': location.longitude}

    except:
        print('No location found')

        return {'latitude': None , 'longitude': None}