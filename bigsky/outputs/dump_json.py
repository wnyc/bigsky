from colorsys import hsv_to_rgb
import boto
import boto.sdb
from csv import DictWriter

import cloudydict
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

import gflags
import time 
import datetime
import json

FLAGS = gflags.FLAGS


gflags.DEFINE_string('domain', 'foliage', 'Domain')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')


def main(argv=None, stdin=None, stdout=None, stderr=None):
    import sys
    argv = argv or sys.argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        argv = FLAGS(argv)[1:]
    except gflags.FlagsError, e:
        stderr.write("%s\\nUsage: %s update_id_addresses\\n%s\n" %
                     (e, sys.argv[0], FLAGS))
        return 1

    simpledb = boto.sdb.connect_to_region(FLAGS.region)
    domain = simpledb.create_domain(FLAGS.domain)



    query = 'select latitude, longitude, datetaken from `' + FLAGS.domain + "` where datetaken like '2013%'"
    cache = {}

    csv = DictWriter(sys.stdout, ('latitude', 'longitude', 'month', 'day', 'dow'))
    csv.writeheader()
    
    for message in domain.select(query):
        if 'datetaken' not in message: continue 
        d = dict(
                latitude=message['latitude'],
                longitude=message['longitude'])
        date = tuple(map(int,message['datetaken'].split()[0].split('-')))
        year, d['month'], d['day'] = date
        if date in cache:
            d['dow'] = cache[date]
        else:
            d['dow'] = datetime.date(*date).isoweekday()
            cache[date] = d['dow']
        csv.writerow(d)
        
