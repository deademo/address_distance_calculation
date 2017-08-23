import urllib.parse
import asyncio
import json
import aiohttp
from pprint import pprint
import diskcache
import os

class movement_type:
    WALKING = 'walking'
    PUBLIC_TRANPORT = 'transit'


class Place:
    def __init__(self, search_string=None, name=None):
        self.search_string = search_string
        self.coords = None
        self.address = None
        self.name = name
        self.nearest_subway_station = None
        self.distance_to_nearest_subway_station = None

    @property
    def repr_data(self):
        data = []
        if self.address is not None:
            data.append('address="{address}"')
        if self.coords is not None:
            data.append('coords="{coords}"')
        if self.search_string is not None:
            data.append('search_string="{search_string}"')
        if self.name is not None:
            data.append('name="{name}"')
        if self.nearest_subway_station is not None:
            data_item = self.nearest_subway_station.name
            if self.distance_to_nearest_subway_station is not None:
                data_item += ", {}".format(self.distance_to_nearest_subway_station)
            data.append('nearest_subway_station="{}"'.format(data_item))
        return data

    def __repr__(self):
        space_prefix_size = 7
        placeholder_str = ',\n{}'.format(' '*space_prefix_size).join(self.repr_data)
        template = '<Place {}>'.format(placeholder_str)
        return template.format(**self.__dict__)

    @property
    def formatted_coords(self):
        if self.coords is not None:
            return '{},{}'.format(*self.coords)
        return self.coords


class SubwayStation(Place):
    pass


class DestinationPlace(Place):
    def __init__(self, *args, mode=movement_type.PUBLIC_TRANPORT, **kwargs):
        self.distance = None
        self.movement_type = mode
        super(DestinationPlace, self).__init__(*args, **kwargs)

    @property
    def repr_data(self):
        data = super(DestinationPlace, self).repr_data
        data.append('distance="{}"'.format(self.distance))
        return data


class Distance:
    def __init__(self):
        self.distance = None
        self.duration = None
        self.type = None

    def __repr__(self):
        return "{:0.2f} км, {:0.0f} мин".format(self.distance/1000, self.duration/60)


class API:
    def __init__(self):
        self.cache_dir = '/tmp/cache'
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_name = 'api_cache'
        self._cache = diskcache.Cache(os.path.join(self.cache_dir, self.cache_name))

    async def request(self, url):
        request_hash = url
        if request_hash in self._cache:
            return self._cache[request_hash]

        connector = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                response = await response.text()
                self._cache[request_hash] = response
                return response


class AddressSearchAPI(API):
    def __init__(self, *args, api_key, loop=None, **kwargs):
        super(AddressSearchAPI, self).__init__(*args, **kwargs)
        self.loop = loop if loop else asyncio.get_event_loop()
        self._maps_api_key = api_key

    async def get_general_info_by_search_string(self, place):
        search_string = place.search_string

        url = 'http://maps.google.com/maps/api/geocode/json?address={address}&language=ru'
        formatted_url = url.format(address=urllib.parse.quote(search_string.encode('utf-8')))
        response = await self.request(formatted_url)
        data = json.loads(response)
        if len(data['results']):
            data = data['results'][0]

            place.address = data['formatted_address']
            place.coords = (data['geometry']['location']['lat'], 
                            data['geometry']['location']['lng'])

        return place

    async def get_destantion(self, origin, destination, mode):
        if isinstance(origin, Place):
            origin = origin.formatted_coords
        if isinstance(destination, Place):
            destination = destination.formatted_coords
        if origin is None or destination is None:
            return None

        url = 'https://maps.googleapis.com/maps/api/distancematrix/{output_type}?origins={origin}&destinations={destination}&mode={mode}&key={key}';
        data = { 'key': self._maps_api_key
               , 'output_type': 'json'
               , 'origin': origin
               , 'destination': destination
               , 'mode': mode}
        formatted_url = url.format(**data);
        response = await self.request(formatted_url);
        data = json.loads(response);
        data = data['rows'][0]['elements']
        if data[0]['status'] == 'ZERO_RESULTS':
            return None

        distance = Distance()
        distance.type = mode
        distance.distance = data[0]['distance']['value']
        distance.duration = data[0]['duration']['value']

        return distance

    async def get_nearest_subway_station(self, place):
        coords = place.formatted_coords
        if not coords:
            return place

        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={key}&location={location}&type=subway_station&rankby=distance&language=ru';
        formatted_url = url.format(key=self._maps_api_key, location=coords);
        response = await self.request(formatted_url);
        data = json.loads(response);
        data = data['results'][0]

        subway_station = SubwayStation()
        subway_station.name = data['name']
        subway_station.coords = (data['geometry']['location']['lat'], 
                                 data['geometry']['location']['lng'])
        place.nearest_subway_station = subway_station

        distance = await self.get_destantion(place, place.nearest_subway_station, movement_type.WALKING)
        place.distance_to_nearest_subway_station = distance

        return place

    async def get_place_by_search_string(self, search_string):
        return await self.get_general_info_by_search_string(Place(search_string))
