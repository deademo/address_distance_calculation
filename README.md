### How i can use it?

1. Setup client using AddressSearchAPI. First parameter must be api key of Google Maps API.
2. Setup your favorite places using DestinationPlace class, where first argumets is address string and second argument is place lable. To this places will be calculated nearest subway station, walking and driving time.
3. Parse your input address using get_place_by_search_string method.
4. Then you can find nearest subway station using method get_nearest_subway_station or calculate movement time using method get_destantion where first parameter it's first place (your parsed string), second parameter it's your favorite place and third parameter it's movement type.

Check out console_interface.py for example.
