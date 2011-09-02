#!/usr/bin/env python

from distutils.core import setup

setup(
    name="python-geocoder",
    version="0.1",
    description="A simple geocoding library using Google Maps APIs",
    long_description=open("README.txt").read(),
    author="Sergiy Kuzmenko",
    author_email="sergiy@kuzmenko.org",
    url="https://bitbucket.org/shelldweller/python-geocoder",
    packages=["geocode"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)