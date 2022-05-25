import requests
import os
from requests.exceptions import ConnectTimeout, ConnectionError, HTTPError, TooManyRedirects, ReadTimeout


def get_city_id(i_city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": i_city, "locale": "ru_RU"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': os.getenv('API_KEY')
    }
    try:
        response = requests.get(url, timeout=10, headers=headers, params=querystring)
        if response.status_code == 200:
            try:
                return response.json()['suggestions'][0]['entities'][0]['destinationId']
            except (ValueError, KeyError, IndexError):
                return None
        else:
            return None
    except (ConnectTimeout, ConnectionError, HTTPError, TooManyRedirects, ReadTimeout):
        return None


def result(i_user, id_city):

    url = "https://hotels4.p.rapidapi.com/properties/list"

    if i_user.command == '/highprice':
        sort_order = 'PRICE_HIGHEST_FIRST'
    else:
        sort_order = 'PRICE'

    if i_user.command == '/highprice' or i_user.command == '/lowprice':

        querystring = {"destinationId": id_city,
                       "pageNumber": "1",
                       "pageSize": i_user.hotels_count, "checkIn": "2020-01-08",
                       "checkOut": "2020-01-15", "adults1": "1", "sortOrder": sort_order, "locale": "ru_RU",
                       "currency": "RUB"}
    else:
        querystring = {"destinationId": id_city,
                       "pageNumber": "1",
                       "pageSize": i_user.hotels_count, "checkIn": "2020-01-08",
                       "checkOut": "2020-01-15", "adults1": "1", "sortOrder": 'DISTANCE_FROM_LANDMARK',
                       "locale": "ru_RU", "currency": "RUB", 'priceMin': int(i_user.price_min),
                       'priceMax': int(i_user.price_max)}

    headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': os.getenv('API_KEY')
    }
    try:
        response_2 = requests.get(url, timeout=10, headers=headers, params=querystring)
        if response_2.status_code == 200:
            if not response_2.json()['data']['body']['searchResults']['results']:
                return '404'
            else:
                try:
                    return response_2.json()['data']['body']['searchResults']['results']
                except (ValueError, KeyError, IndexError):
                    return None
        else:
            return None
    except (ConnectTimeout, ConnectionError, HTTPError, TooManyRedirects, ReadTimeout):
        return None


def photos(i_id):

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": i_id}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': os.getenv('API_KEY')
    }
    try:
        response = requests.request("GET", url, timeout=10, headers=headers, params=querystring)

        if response.status_code == 200:
            try:
                return response.json()['hotelImages']
            except (ValueError, KeyError, IndexError):
                return None
        else:
            return None
    except (ConnectTimeout, ConnectionError, HTTPError, TooManyRedirects, ReadTimeout):
        return None