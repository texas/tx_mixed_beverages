import os
from typing import Dict

import requests


# DEPRECATED, use Geodude service directly instead
def get_remaining_credits():
    # if you run out of credits, go to
    # https://geoservices.tamu.edu/UserServices/Payments/
    api_key = os.environ.get('TAMU_API_KEY')
    assert api_key
    url = ('https://geoservices.tamu.edu/UserServices/Payments/Balance/'
    'AccountBalanceWebServiceHttp.aspx?'
    'version=1.0&apikey={}&format=csv'.format(api_key))
    response = requests.get(url)
    assert response.ok
    key, credits = response.text.split(',')
    assert key == api_key
    return int(credits)


class GeocodeException(Exception):
    pass


def geocode_address(address: Dict, force: bool=False) -> Dict:
    """
    Geocode an address dict.

    Address dict should have the keys: address, city, state, zipcode

    Examples:
    http://geoservices.tamu.edu/Services/Geocode/WebService/v04_01/Simple/Rest/
    """
    if not address['city'] and not address['zipcode']:
        raise GeocodeException("Can't look up without a city or zip")
    geodude_url = os.getenv('GEODUDE_URL')
    params = {
        'address': address['address'],
        'city': address['city'],
        'state': address['state'],
        'zip': address['zipcode'],
    }
    headers = {
        'user-agent': 'default/lazy_geo v0.0'
    }
    response = requests.get('{}/tamu'.format(geodude_url), params=params, headers=headers)
    if not response.ok:
        raise GeocodeException('Got a non-200 response: {}'.format(response.status_code))
    return response.json()
