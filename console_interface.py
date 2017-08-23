from api import AddressSearchAPI, DestinationPlace
import asyncio
import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    search_string = input('Введите адрес:\n')
    cls()

    places = [DestinationPlace('Шота Руставели 27Б, Киев', 'Работа'),
              DestinationPlace('станция метро Академгородок', 'Академгородок'),
              DestinationPlace('Богдановская 10, Киев', 'Пред. дом (богдановская 10)'),
              DestinationPlace('станция метро Вокзальная', 'Вокзальная'),]
    
    loop = asyncio.get_event_loop()
    api = AddressSearchAPI()

    place = loop.run_until_complete(api.get_place_by_search_string(search_string))
    place = loop.run_until_complete(api.get_nearest_subway_station(place))
    print('Искомое место: {}'.format(place.address))
    print('Ближайшая стацния метро:\n\n{}, {} пешком\n'.format(place.nearest_subway_station.name, place.distance_to_nearest_subway_station))

    print('Время до мест:')
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