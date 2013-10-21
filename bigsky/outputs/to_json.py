from colorsys import hsv_to_rgb
import boto
import boto.sdb

import cloudydict
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

import gflags
import time 
import datetime
import json

FLAGS = gflags.FLAGS


gflags.DEFINE_string('domain', 'foliage', 'Domain')
gflags.DEFINE_boolean('delete', False, 'Remove items from queue when done processing?')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('target', 'wnyc.org-foliage-public', 'S3 target')


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


    data = []
    by_date = {argv[0]:data}

    query = 'select * from `' + FLAGS.domain + "` where outside is not null and  treehue is not null and datetaken like '" + argv[0] + "%'"
    for message in domain.select(query):
        if 'outside' not in message:
            continue 
        try:
            message['latitude'] = float(message['latitude'])
            message['longitude'] = float(message['longitude'])
            if message['latitude'] == 0 and message['longitude'] == 0:
                continue 
            datum = {}
            hues = []
            datum['hues'] = hues
            datum['lat'] = message['latitude']
            datum['long'] = message['longitude']
            datum['url'] = message['url_s']
            datum['source'] = 'flickr'
            for key in sorted(message):
                if key.startswith('hue'):
                    hues.append(float(message[key]))
            if not hues: continue 

            greens = hues[9:16]
            yellows = hues[:9]
            
            c = 0.0
            v = 0.0
            for hue, level in enumerate(hues[:16]):
                c += level
                v += hue * level
            
            avg = v / c
            avg *= 10
            datum['avghue'] = int(message['treehue'])
            datum['hex'] = message['hexagon']
            datum['color'] = '#%02x%02x%02x' % hsv_to_rgb(avg / 36.0, 0.5, 0.8)
            if yellows > 0.2 or greens > 0.2:
                data.append(datum)
        except:
            raise
            
    d = cloudydict.factory('s3:' + FLAGS.target)()
    d[argv[0]] = json.dumps(by_date)
    d[argv[0]].make_public()
    print by_date
    print len(by_date.values()[0])
