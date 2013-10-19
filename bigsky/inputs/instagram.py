import gflags
import boto
import boto.sqs
from boto.sqs.message import Message
import json

FLAGS = gflags.FLAGS
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('target', None, 'Select SQS queue target')

import web

urls = (
    '/', 'index'
)

class index:
    def GET(self):
        data = web.input()
        return data['hub.challenge']


    def POST(self):
        global q
        data = web.data()
        print data
        m = Message() 
        m.set_body(data)
        q.write(m)


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
    global q

    sys.argv = [sys.argv[0]]
    sys.argv.extend(argv)
    conn = boto.sqs.connect_to_region(FLAGS.region)
    q = conn.create_queue(FLAGS.target)
    
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
