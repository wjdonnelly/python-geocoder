#!/usr/bin/env python
"""
Command line interface fro Google geocoding service.
"""

from geocode.google import GoogleGeocoder, GoogleGeocoderClient

def main():
    """Command line interface that outputs geocoding results in json format."""
    import sys
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("-a", "--address", dest="address", default=None)
    parser.add_option("-p", "--latlng", dest="latlng", default=None, help="comma separated latitude and longitude")
    parser.add_option("-b", "--bounds", dest="bounds", default=None)
    parser.add_option("-r", "--region", dest="region", default=None)
    parser.add_option("-l", "--language", dest="language", default=None)
    parser.add_option("-s", "--sensor", dest="sensor", default=False)
    parser.add_option("-o", "--output", dest="output", default="json")
    parser.add_option("--raw", dest="raw", action="store_true", default=False, help="output raw results in json format.")
    
    (options, args) = parser.parse_args()
    
    str2tuple = lambda x: tuple(map(lambda y:int(y), x.split(",")))
    
    latlng = None
    bounds = None
    
    if options.latlng:
        latlng = str2tuple(options.latlng)
    if options.bounds:
        bounds = map(lambda x:str2tuple(x), options.bounds.split("|"))
    
    geocoder = GoogleGeocoderClient(bool(options.sensor))
    try:
        json_data = geocoder.geocode_raw(
            options.output, options.address, options.latlng, options.bounds, \
            options.region, options.language)
    except AssertionError, e:
        sys.stderr.write("ERROR: %s\n"%e)
        sys.exit(1)
    
    if options.raw:
        print json_data
    else:
        results = GoogleGeocoder(json_data)
        if results.is_success():
            for result in results:
                print "%s (%s, %s) - %s" % (result["formatted_address"],
                                            result["geometry"]["location"]["lat"],
                                            result["geometry"]["location"]["lng"],
                                            result["geometry"]["location_type"])
        else:
            print results.data["status"]

if __name__ == "__main__":
    main()
