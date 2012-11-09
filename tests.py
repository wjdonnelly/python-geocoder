#!/usr/bin/env python

import unittest
from decimal import Decimal
from geocode.google import GoogleGeocoder, GoogleGeocoderClient

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
        
    def test_number_of_results(self):
        self.assertTrue(len(self.geocoder.results) == 1)
    
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


if __name__ == '__main__':
    unittest.main()
