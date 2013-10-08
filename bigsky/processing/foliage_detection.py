import Image
from StringIO import StringIO 
import sys 
import boto
import boto.sdb
import boto.sqs
import boto.s3
import json
import gflags
from fractions import Fraction
from colorsys import rgb_to_hls
FLAGS = gflags.FLAGS

gflags.DEFINE_string('source', None, 'Source SQS queue to read from')
gflags.RegisterValidator('source', lambda x:x is not None, 'You must specify a source queue')
gflags.DEFINE_multistring('targets', [], 'Select SQS queue target')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('bucket', 'wnyc.org-foliage-exif', 'bucket to read from')
gflags.RegisterValidator('bucket', lambda x:x is not None, 'You must specify a bucket')
gflags.DEFINE_string('domain', 'foliage', 'Domain')

def compute_histogram(items):
    histo = {}
    for item in items:
        if item is None: continue 
        if item in histo:
            histo[item] += 1
        else:
            histo[item] = 1
    return histo

def extract_hue(v):
    if max(v) == min(v):
        return None
    
    hue, l, s = rgb_to_hls(*[x / 256.0 for x in v])
    hue *= 360

    
    if 0 < hue <= 140 or hue>=330:
        if s > 0.6:
            return 'foliage'
        else:
            return 'other'
    if hue < 190:
        return 'green'
    return 'other' 


    

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
            image = Image.open(StringIO(bucket.get_key(message['id']).get_contents_as_string()))
            image = image.resize((64,64))
            x, y = image.size
            size = float(x * y)
            histogram = compute_histogram(map(extract_hue, image.getdata()))
            item = domain.get_item(message['id'])
            item['foliage'] = histogram.get('foliage', 0) / size
            item['green'] = histogram.get('green', 0) / size
            item['other'] = histogram.get('other', 0) / size
            item.save()
            for target in targets:
                target.write(incoming)
            q.delete_message(incoming)
        messages = q.get_messages()


    return 0
        
