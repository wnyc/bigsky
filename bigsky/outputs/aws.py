import boto

from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

import gflags
import time 
import datetime
import json

FLAGS = gflags.FLAGS


gflags.DEFINE_string('source', None, 'Select SQS queue source')
gflags.DEFINE_boolean('delete', False, 'Remove items from queue when done processing?')
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
    sqs = boto.sqs.connect_to_region(FLAGS.region)
    q = conn.create_queue(FLAGS.source)
    simpledb = boto.sdb.connect_to_region(FLAGS.region)
    domain = simpledb.create_domian('foliage')
    
    incomings = q.get_messages()
    while incomings:
        for incoming in incomings:
            message = json.loads(incoming.get_body())
            domain.put_attributes(message['id'], message)
        incomings = q.get_messages()
            
