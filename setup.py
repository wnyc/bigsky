#!/usr/bin/env python

"""
bigsky
=================
WNYC's "bigsky" big data image processing initiative.
"""

from setuptools import setup

setup(
    name='bigsky',
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description="WNYC's big data image processing toolkit",
    long_description=__doc__,
    url="http://github.com/wnyc/bigsky",
    py_modules=[
        'bigsky/__init__',
        'bigsky/inputs/__init__',
        'bigsky/inputs/reader',
        'bigsky/inputs/flickr',
        'bigsky/inputs/instagram',
        'bigsky/exif/__init__',
        'bigsky/editor/__init__',
        'bigsky/editor/picker',
        'bigsky/outputs/__init__',
        'bigsky/outputs/dump_json',
        'bigsky/outputs/to_googlemap',
        'bigsky/outputs/to_json',
        'bigsky/outputs/simpledb_import',
        'bigsky/outputs/simpledb_output',
        'bigsky/outputs/s3_to_sqs',
        'bigsky/outputs/s3_import',
        'bigsky/outputs/exiv2',      
        'bigsky/processing/outside',
        'bigsky/processing/mark_known_outside',
        'bigsky/processing/__init__',
        'bigsky/processing/foliage_detection',
        'bigsky/processing/find_closest_hex',
        ],
    packages=['bigsky',],
    zip_safe=True,
    license='MIT',
    include_package_data=True,
    classifiers=[],
    scripts=['scripts/bigsky_spider', 
             'scripts/bigsky_exif', 
             'scripts/bigsky_html', 
             'scripts/bigsky_picker',
             'scripts/bigsky_simpledb_import', 
             'scripts/bigsky_s3_import', 
             'scripts/bigsky_simpledb_output',
             'scripts/bigsky_to_json',
             'scripts/bigsky_to_googlemap',
             'scripts/bigsky_exiv2', 
             'scripts/bigsky_dump_json', 
             'scripts/bigsky_s3_to_sqs',
             'scripts/bigsky_outside_only', 
             'scripts/bigsky_mark_known_outside',
             'scripts/bigsky_foliage_detection',
             'scripts/bigsky_slurp_instagram',
             'scripts/bigsky_find_closest_hex',
             ],

    install_requires=[
        'python-gflags',
        'boto>=2.13.3',
        'PIL',
        'requests',
        'cloudydict',
        'flickrapi>=1.4.2',
        'PIL>=1.1.7',
        'wsgiref>=0.1.2',
        'web.py',
        ]
    )
