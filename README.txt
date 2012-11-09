About
=====

Python-Geocoder is a simple library that uses Google Maps API for geocoding.


Usage
=====

As python library::

    >>> from geocode.google import GoogleGeocoderClient
    
    >>> geocoder = GoogleGeocoderClient(False) # must specify sensor parameter explicitely
    >>> result = geocoder.geocode("massasauga park")
    
    >>> result.is_success()
    True
    
    >>> len(result)
    3
    
    # by default all get_*() methods will fetch the first result:
    >>> result.get_formatted_address()
    u'The Massasauga Provincial Park, The Archipelago, ON, Canada'
    
    # but you can also pass it an index parameter:
    >>> result.get_formatted_address(2)
    u'Massasauga Prairie Nature Preserve, Roseville, IL 61417, USA'
    
    >>> result.get_location()
    (Decimal('45.19526590'), Decimal('-80.05372229999999'))
    
    >>> result.get_location_type()
    u'APPROXIMATE'
    
    # each result object is an iterator containing nested dictionaries according to
    # Google geocoding specifications (http://code.google.com/apis/maps/documentation/geocoding/)
    >>> for r in result: print r["formatted_address"]
    The Massasauga Provincial Park, The Archipelago, ON, Canada
    The Massasauga Provincial Park, RR 2, Parry Sound, ON P0G, Canada
    Massasauga Prairie Nature Preserve, Berwick, IL 61417, USA


If you are using Google Maps API for business pass your key and client id when
initializing GoogleGeocoderClient::

    >>> geocoder = GoogleGeocoderClient(False, my_client_id, my_key)
    

geocode/google-geocoder.py is a command line tool. A sample usage::

    $ python geocode/google.py -a "massasauga park"
    The Massasauga Provincial Park, The Archipelago, ON, Canada (45.19526590, -80.05372229999999) - APPROXIMATE
    The Massasauga Provincial Park, RR 2, Parry Sound, ON P0G, Canada (45.1969970, -80.0398220) - APPROXIMATE
    Massasauga Prairie Nature Preserve, Roseville, IL 61417, USA (40.76002530, -90.57780330) - APPROXIMATE

For more usage information run::

    $ python geocode/google.py --help
