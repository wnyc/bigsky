import boto
import boto.sqs
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

def compute_light_level(stuff):
    needs = {'Exif.Photo.ISOSpeedRatings': None,
             'Exif.Photo.FNumber': None,
             'Exif.Photo.ExposureTime': None,}
    stuff = stuff.split('\n')
    for row in stuff:
        try:
            field, stuff = row.split(None, 1)
        except ValueError:
            return None
        if field in needs:
            needs[field] = stuff
    if None in needs.values():
        return None
    try:
        f = float(needs['Exif.Photo.FNumber'].split()[-1].replace('F',''))
        iso = float(needs['Exif.Photo.ISOSpeedRatings'].split()[-1])
        shutter = Fraction(needs['Exif.Photo.ExposureTime'].split()[-2])
    except:
        return None
    try:
        level = float(f*f / (iso * shutter))
    except ZeroDivisionError:
        return None

    print level
    return level

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
    while messages:
        for incoming in messages:
            message = json.loads(incoming.get_body())
            
            level = compute_light_level(bucket.get_key(message['id']).get_contents_as_string())
            if level is not None and level >= FLAGS.threshold:
                for target in targets:
                    target.write(incoming)
            q.delete_message(incoming)
        messages = q.get_messages()


    return 0
        
