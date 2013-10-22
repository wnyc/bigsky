import boto
import boto.sdb
from colorsys import rgb_to_hsv

from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

import gflags
import time 
import datetime
import json

FLAGS = gflags.FLAGS


gflags.DEFINE_string('source', None, 'Select SQS queue source')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('domain', 'foliage', 'Domain')

def color(hue):
    return rgb_to_hsv(hue / 360.0, 1.0, 1.0)


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

    print """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <style type="text/css">
      html { height: 100% }
      body { height: 100%; margin: 0; padding: 0 }
      #map-canvas { height: 100% }
    </style>
    <script type="text/javascript"
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAzc0NxoydaK4dD-Gz-bJhXtsIqXvbgvoQ&sensor=true">
    </script>
    <script type="text/javascript">
      function initialize() {
        var mapOptions = {
          center: new google.maps.LatLng(39.8282, -95.5795),
          zoom: 4,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById("map-canvas"),
            mapOptions);
"""
    sdb = boto.sdb.connect_to_region(FLAGS.region)
    domain = sdb.create_domain(FLAGS.domain)

    query = 'select * from `' + FLAGS.domain + "` where  tree is not null and datetaken like '" + argv[0] + "%'"
    for message in domain.select(query):
        try:
            if not message.get('tree') or not message.get('url_z'):
                continue 
            message['latitude'] = float(message['latitude'])
            message['longitude'] = float(message['longitude'])
            message['avghue'] = int(message['treehue'])
            if message['latitude'] == 0 and message['longitude'] == 0:
                continue 

            print   """
marker = new google.maps.Marker({
        position: new google.maps.LatLng(%(latitude)f, %(longitude)f),
        map: map,
        url:"%(url_z)s",
        icon:new google.maps.MarkerImage("%(avghue)d.png"),
        flat:true,
        optimized:false, 
      });

google.maps.event.addListener(marker, 'click', function() {
    window.location.href = this.url;
});

""" % message
        finally:
            pass
    print """
  }
      google.maps.event.addDomListener(window, 'load', initialize);
   </script>
  </head>
  <body>
    <div id="map-canvas"/>
  </body>
</html>
"""
            
