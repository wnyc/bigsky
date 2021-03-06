import boto
import boto.sdb
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

import gflags
import time 
import datetime
import json

FLAGS = gflags.FLAGS


gflags.DEFINE_multistring('targets', [], 'Select SQS queue target')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('bucket', None, 'bucket to read from')
gflags.RegisterValidator('bucket', lambda x:x is not None, 'You must specify a bucket')
gflags.DEFINE_string('domain', 'foliage', 'Domain')

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
    sqs = boto.sqs.connect_to_region(FLAGS.region)
    targets = map(sqs.create_queue, FLAGS.targets)
    simpledb = boto.sdb.connect_to_region(FLAGS.region)
    domain = simpledb.create_domain(FLAGS.domain)
    bucket = boto.s3.connect_to_region(FLAGS.region).get_bucket(FLAGS.bucket)
    print "Fetching existing keys"
    keys = set(k.key for k in bucket.list())
    print "Retriving database contents"
    for row in domain.select('select * from `' + FLAGS.domain + '`'):
        if row['id'] not in keys:
            print "Rejecting", row['id']
            continue 
        print "Accepting", row['id']
        m = Message()
        m.set_body(json.dumps(row))
        for target in targets:
            target.write(m)
        
            

