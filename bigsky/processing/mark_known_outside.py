import boto
import boto.sqs
import boto.sdb
import boto.s3
import json
import gflags
from fractions import Fraction
FLAGS = gflags.FLAGS

gflags.DEFINE_string('source', None, 'Source SQS queue to read from')
gflags.RegisterValidator('source', lambda x:x is not None, 'You must specify a source queue')
gflags.DEFINE_multistring('targets', [], 'Select SQS queue target')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('bucket', 'wnyc.org-foliage-exif', 'bucket to read from')
gflags.RegisterValidator('bucket', lambda x:x is not None, 'You must specify a bucket')
gflags.DEFINE_string('domain', None, 'Domain')
gflags.DEFINE_float('threshold', 5.0, 'Brightness threshold for outdoors')



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
    if FLAGS.domain is not None:
        simpledb = boto.sdb.connect_to_region(FLAGS.region)
        domain = simpledb.create_domain(FLAGS.domain)
    else:
        domain = None
    bucket = boto.s3.connect_to_region(FLAGS.region).get_bucket(FLAGS.bucket)

    q = sqs.get_queue(FLAGS.source)
    messages = q.get_messages()
    batch = {}
    delete = []
    while messages:
        for incoming in messages:
            message = json.loads(incoming.get_body())
            print message['id']
            batch[message['id']] = {'outside':'true'}
            delete.append(incoming)
            if len(batch) >= 25:
                domain.batch_put_attributes(batch)
                for deleted in delete:
                    for target in targets:
                        target.write(deleted)
                    q.delete_message(deleted)
                batch = {}
                delete = []
        messages = q.get_messages()
    if batch:
        domain.batch_put_attributes(batch)
    for deleted in delete:
        for target in targets:
            target.write(deleted)
        q.delete_message(deleted)


    return 0
        
