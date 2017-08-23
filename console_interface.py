from api import AddressSearchAPI, DestinationPlace
import asyncio
import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    search_string = input('Input address:\n')
    cls()

    places = [DestinationPlace('Someone Adrres, 77a', 'Work'),]
    
    loop = asyncio.get_event_loop()
    api = AddressSearchAPI()

    place = loop.run_until_complete(api.get_place_by_search_string(search_string))
    place = loop.run_until_complete(api.get_nearest_subway_station(place))
    print('Searching address: {}'.format(place.address))
    print('Nearest subway station:\n\n{}, {} walking\n'.format(place.nearest_subway_station.name, place.distance_to_nearest_subway_station))

    print('Movement time:')
    for place_index in range(len(places)):
        places[place_index] = loop.run_until_complete(api.get_general_info_by_search_string(places[place_index]))
        places[place_index].distance = loop.run_until_complete(api.get_destantion(place, places[place_index], places[place_index].movement_type))
        print('{} - {}'.format(places[place_index].name, places[place_index].distance))
    print('')

if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            pass