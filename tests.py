#!/usr/bin/env python

import unittest
from decimal import Decimal
from geocode.google import GoogleGeocoder, GoogleGeocoderClient, GOOGLE_GEOCODING_API_URL
from urlparse import urlparse

class GoogleGeocoderValidAddressTests(unittest.TestCase):
    """
    Tests will fail if there is a network problem, such as misconfigured
    proxy or no connection.
    """
    
    def setUp(self):
        self.address = "1 Front Street West, Toronto, ON"
        self.region = "CA"
        
        client = GoogleGeocoderClient(sensor=False)
        data = client.geocode_raw("json", self.address, region=self.region)
        
        self.geocoder = GoogleGeocoder(data)
    
    def test_success(self):
        self.assertTrue(self.geocoder.is_success())
        
    def test_formatted_address(self):
        self.assertTrue("Toronto" in self.geocoder.get_formatted_address())
    
    def test_location_type(self):
        location_type = self.geocoder.get_location_type()
        expected_location_type = "ROOFTOP"
        self.assertTrue(location_type == expected_location_type,
                        "Unexpected location_type: got `%s` but expecting `%s`" % \
                        (location_type, expected_location_type))
        
    def test_location(self):
        (lat, lng) = self.geocoder.get_location()
        expected_lat = Decimal("43.6463685")
        expected_lng = Decimal("-79.3770610")
        self.assertTrue(lat == expected_lat, "Expecting latitude `%s` but got `%s`" % (expected_lat, lat))
        self.assertTrue(lng == expected_lng, "Expecting longitude `%s` but got `%s`" % (expected_lng, lng))


class GoogleGeocoderClientTests(unittest.TestCase):
    """ Test GoogleGRocoderClient """
    
    def _get_params(self, url):
        # parses url and returns query params as a dictionary
        parsed_url = urlparse(url)
        return dict(map(lambda x:x.split("=", 1), parsed_url.query.split("&")))
        
    
    def test_signed_request(self):
        """ Test that signing is performed correctly when using Google Maps API
        for Business
        """
        # based on the example from
        # https://developers.google.com/maps/documentation/business/webservices#signature_examples
        
        CLIENT_ID = 'clientID'
        
        client = GoogleGeocoderClient(
            False, client=CLIENT_ID, key='vNIXE0xscrmjlyV-12Nj_BvUPaw='
        )
        url = client._build_request("json", "New York", None, None, None, None)
        params = self._get_params(url)
        
        self.assertIn('client', params)
        self.assertIn('signature', params)
        self.assertEqual(params['client'], CLIENT_ID)
        self.assertEqual(params['signature'], 'KrU1TzVQM7Ur0i8i7K3huiw3MsA=')
    
    def test_unsigned_request(self):
        """ Test that request is not signed when NOT using Google Maps API
        for Business
        """
        
        client = GoogleGeocoderClient(False)
        url = client._build_request("json", "New York", None, None, None, None)
        params = self._get_params(url)
        
        self.assertNotIn('client', params)
        self.assertNotIn('signature', params)
    

if __name__ == '__main__':
    unittest.main()
