import os

from django.core.exceptions import ImproperlyConfigured
import requests


class GeocodeException(Exception):
    pass


def geocode_address(address, force=False):
    """
    Geocode an address dict.

    Address dict should have the keys: address, city, state, zipcode

    Examples:
    http://geoservices.tamu.edu/Services/Geocode/WebService/v04_01/Simple/Rest/
    """
    if not address['city'] and not address['zipcode']:
        raise GeocodeException("Can't look up without a city or zip")
    api_key = os.environ.get('TAMU_API_KEY')
    if not api_key:
        raise ImproperlyConfigured(
            "Can't look up without 'TAMU_API_KEY' environment variable")
    url = (
        'http://geoservices.tamu.edu/Services/Geocode/WebService/'
        'GeocoderWebServiceHttpNonParsed_V04_01.aspx'
    )
    params = {
        'apiKey': api_key,
        'version': '4.01',
        'streetAddress': address['address'],
        'city': address['city'],
        'state': address['state'],
        'zip': address['zipcode'],
    }
    headers = {
        'user-agent': 'default/lazy_geo v0.0'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise GeocodeException('Got a non-200 response: {}'
            .format(response.status_code))
    fields = [
        'TransactionId',
        'Version',
        'QueryStatusCodeValue',
        'Latitude',
        'Longitude',
        'NAACCRGISCoordinateQualityCode',
        'NAACCRGISCoordinateQualityName',
        'MatchScore',
        'MatchType',
        'FeatureMatchingResultType',
        'FeatureMatchingResultCount',
        'FeatureMatchingGeographyType',
        'RegionSize',
        'RegionSizeUnits',
        'MatchedLocationType',
        'TimeTaken',
    ]
    return dict(zip(fields, response.text.split(',')))
