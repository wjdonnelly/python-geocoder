import hashlib
import hmac
import base64
import urlparse

from decimal import Decimal

try:
    from urllib2 import urlopen
except ImportError:
    from urllib import urlopen # urllib.urlopen was deprecated in 2.6
from urllib import quote_plus

try:
    import json # 2.6 or newer
except ImportError:
    import simplejson as json

GOOGLE_GEOCODING_API_URL = "http://maps.googleapis.com/maps/api/geocode/"
LAT = 0 # latitude
LNG = 1 # longitude


class GoogleGeocoder(object):
    """
    GoogleGeocoder is a convenience class defining a number of shortcut
    methods for reading geocoding data in json format.
    
    http://code.google.com/apis/maps/documentation/geocoding/#Results
    
    """
    def __init__(self, data):
        """
        You can initialize GoogleGeododer manually by feeding it raw json data
        or initialize it implicitely from a geocode() call to an instance of
        GoogleGeocoderClient:
        
        >>> client = GoogleGeocoderClient(False)
        >>> result = client.geocode("massasauga park")
        
        AssertionError will be raised if data is not a valid Google geocoding
        JSON serialization.
        """
        
        self.data = json.loads(data, parse_float=Decimal)
        try:
            assert "status" in self.data and "results" in self.data
        except AssertionError:
            raise AssertionError("Invalid JSON data: expecting dictionary with 'status' and 'results' keys")
        
    def __iter__(self):
        return iter(self.results)
    
    def __len__(self):
        return len(self.results)
    
    def __getitem__(self, i):
        return self.results[i]
    
    def is_success(self):
        """Whether or not geocoding was succesfull."""
        return self.data["status"] == "OK"
    
    @property
    def results(self):
        """
        Returns results list. For details see
        http://code.google.com/apis/maps/documentation/geocoding/#Results
        """
        return self.data["results"]
    
    def get_formatted_address(self, id=0):
        """
        Returns formatted address for result specified by id (defaults to  the
        first result):
        
        >>> result = GoogleGeocoderClient(False).geocode("massasauga park")
        >>> result.get_formatted_address()
        u'The Massasauga Provincial Park, The Archipelago, ON, Canada'
        >>> result.get_formatted_address(-1) # last result
        u'Massasauga Prairie Nature Preserve, Roseville, IL 61417, USA'
        """
        return self.data["results"][id]["formatted_address"]
    
    def get_location(self, id=0):
        """
        Returns a tuple of Decimals (lat, lng) representing address location
        for result specified by id (first result by default):
        
        >>> result = GoogleGeocoderClient(False).geocode("massasauga park")
        >>> result.get_location()
        (Decimal('45.19526590'), Decimal('-80.05372229999999'))
        """
        return (
            Decimal(self.data["results"][id]["geometry"]["location"]["lat"]),
            Decimal(self.data["results"][id]["geometry"]["location"]["lng"]),
            )
    
    def get_location_type(self, id=0):
        """
        Returns location type for result specified by id (first result by default):
        
        >>> result = GoogleGeocoderClient(False).geocode("massasauga park")
        >>> result.get_location_type()
        u'APPROXIMATE'
        """
        return self.data["results"][id]["geometry"]["location_type"]
    
    def get_address_component(self, component_type, id=0, long_name=False):
        """
        Returns the first matching address component of specified type. If id is
        not specified, the first result will be examined. If component type is
        not found None will be returned:
        
        >>> result = GoogleGeocoderClient(False).geocode("massasauga park")
        >>> result.get_address_component("country")
        u'CA'
        
        >>> result.get_address_component("country", long_name=True)
        u'Canada'
        
        >>> result.get_address_component("invalid compoment") # returns None
        """
        key = "short_name"
        if long_name:
            key = "long_name"
        for ac in self.data["results"][id]["address_components"]:
            for t in ac["types"]:
                if component_type == t:
                    return ac[key]
        return None

    def get_address_components(self, component_type, id=0, long_name=False):
        """
        Like get_address_component but returns all matching components:
        
        >>> result = GoogleGeocoderClient(False).geocode("massasauga park")
        >>> result.get_address_components("political")
        [u'The Archipelago', u'Parry Sound District', u'ON', u'CA']
        
        >>> result.get_address_components("political", long_name=True)
        [u'The Archipelago', u'Parry Sound District', u'Ontario', u'Canada']
        
        >>> result.get_address_components("invalid compoment")
        []
        """
        results = []
        key = "short_name"
        if long_name:
            key = "long_name"
        for ac in self.data["results"][id]["address_components"]:
            for t in ac["types"]:
                if component_type == t:
                    results.append(ac[key])
        return results

class GoogleGeocoderClient(object):
    
    def __init__(self, sensor, client=None, key=None):
        """
        Sensor parameter is boolean, for details see:
        http://code.google.com/apis/maps/documentation/geocoding/

        `client` and `key` parameters are for use by Google Maps API for
        Business users. See
        https://developers.google.com/maps/documentation/business/webservices
        for more information.

        """
        self.sensor = sensor
        self.client = client
        self.key = key

    def _build_request(self, output, address, latlng, bounds, region, language):
        """Helper function for building the request URL.

        >>> client = GoogleGeocoderClient(False)
        >>> args = ('json', 'New York', None, None, None, None)
        >>> url = urlparse.urlparse(client._build_request(*args))
        >>> sigs = filter(lambda x: x[:10] == 'signature=', url.query.split('&'))
        >>> print len(sigs)
        0

        >>> client = GoogleGeocoderClient(
        ...     False, client='clientID', key='vNIXE0xscrmjlyV-12Nj_BvUPaw='
        ... )
        >>> args = ('json', 'New York', None, None, None, None)
        >>> url = urlparse.urlparse(client._build_request(*args))
        >>> sigs = filter(lambda x: x[:10] == 'signature=', url.query.split('&'))
        >>> print len(sigs)
        1
        >>> print sigs[0][10:]
        KrU1TzVQM7Ur0i8i7K3huiw3MsA=

        """
        if (not (address or latlng)) or (address and latlng):
            raise AssertionError("Either address or latlang is required (but not both)")
        assert output in ("json", "xml")

        tuple2str = lambda x: "%s,%s" % (x[0], x[1])

        bool2str = lambda x:str(bool(x)).lower()

        params = []

        if address:
            if isinstance(address, unicode):
                params.append("address=" + quote_plus(address.encode("utf8")))
            else:
                params.append("address=" + quote_plus(address))

        params.append("sensor=" + bool2str(self.sensor))

        if latlng:
            params.append("latlng=" + tuple2str(latlng))
        if bounds:
            params.append("bounds=" + "|".join(map(lambda x:tuple2str(x), bounds)))
        if region:
            params.append("region=" + quote_plus(region))
        if language:
            params.append("language=" + quote_plus(language))
        if self.client:
            params.append("client=" + self.client)

        req = GOOGLE_GEOCODING_API_URL + output + "?" + "&".join(params)
        return self._sign_request(req)

    def _sign_request(self, req):
        """For Google Maps API for Business requests.

        Largely borrowed from
        http://gmaps-samples.googlecode.com/svn/trunk/urlsigning/urlsigner.py

        """
        if not self.client or not self.key:
            return req

        url = urlparse.urlparse(req)

        # We only need to sign the path+query part of the string
        urlToSign = url.path + "?" + url.query

        # Decode the private key into its binary format
        decodedKey = base64.urlsafe_b64decode(self.key)

        # Create a signature using the private key and the URL-encoded
        # string using HMAC SHA1. This signature will be binary.
        signature = hmac.new(decodedKey, urlToSign, hashlib.sha1)

        # Encode the binary signature into base64 for use within a URL
        encodedSignature = base64.urlsafe_b64encode(signature.digest())
        originalUrl = url.scheme + "://" + url.netloc + url.path + "?" + url.query
        return originalUrl + "&signature=" + encodedSignature
    
    def geocode_raw(self, output="json", address=None, latlng=None, bounds=None, region=None, language=None):
        """ Returns raw geocoded address information in json or xml format.
        Arguments:
        output - "json" or "xml"
        address - street address (e.g., 123 Main Street)
        latlng - a tuple for latiture/longitude (expressed as Decimal or float)
        bounds - an iterable whose elements are latlng tuples
        region - ccTLD country/region name (e.g., "CA" for Canada)
        language - language in which return results (e.g., "fr" for French)
        
        Either address or latlng (but not both) parameters are required. the rest is optional.
        """
        url = self._build_request(output, address, latlng, bounds, region, language)
        handler = urlopen(url)
        return handler.read()
    
    def geocode(self, address=None, latlng=None, bounds=None, region=None, language=None):
        """ Returns an instance of GoogleGeocoder. """
        return GoogleGeocoder(self.geocode_raw("json", address, latlng, bounds, region, language))



if __name__ == "__main__":
    import doctest
    doctest.testmod()
