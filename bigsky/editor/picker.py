#!/usr/bin/env python     
import Tkinter as tk      
import urllib2
from colorsys import rgb_to_hsv
import Image
import ImageTk
import gflags
import json
import Queue
import boto
import boto.sdb

import cloudydict
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from StringIO import StringIO 

FLAGS = gflags.FLAGS

from threading import Thread

gflags.DEFINE_string('domain', 'foliage', 'Domain')
gflags.DEFINE_integer('prefetch', 20, 'Images to prefetch')
gflags.DEFINE_boolean('delete', False, 'Remove items from queue when done processing?')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('source', 'foliage-outdoors4', 'Source queue for images')


class Reader(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self._queue = queue
        self.daemon = True


    def run(self):

        try:
            self.simpledb = boto.sdb.connect_to_region(FLAGS.region)
            self.domain = self.simpledb.create_domain(FLAGS.domain)
            sqs = boto.sqs.connect_to_region(FLAGS.region)
            q = sqs.create_queue(FLAGS.source)
            incomings = q.get_messages()
            while incomings:
                for incoming in incomings:
                    print "Incoming"
                    message = json.loads(incoming.get_body())
                    row = self.domain.get_item(message['id'])
                    if 'tree' in row or 'url_z' not in row:
                        q.delete_message(incoming)
                        continue 
                    image = StringIO(urllib2.urlopen(message['url_z']).read())
                self._queue.put((message, incoming, image))
                incomings = q.get_messages()
        finally:
            self._queue.put(None)

                        
        

class Application(tk.Frame):              
    def __init__(self, master=None):
        self.q = Queue.Queue(maxsize=FLAGS.prefetch)

        self.downloader = Reader(self.q)
        self.downloader.start()

        tk.Frame.__init__(self, master)   
        self.grid()                       
        self.createWidgets()

        self.simpledb = boto.sdb.connect_to_region(FLAGS.region)
        self.domain = self.simpledb.create_domain(FLAGS.domain)
        self.sqs = boto.sqs.connect_to_region(FLAGS.region)
        self.sqs_q = self.sqs.create_queue(FLAGS.source)

        self.original = None
        self.next()

    def next(self, datum=None):
        if datum and self.message:
            print "Adding ", datum," to ", self.message['id']
            self.domain.put_attributes(self.message['id'], datum)

        self.message = self.q.get()
        if self.original is not None:
            print "Removing message from queue"
            self.sqs_q.delete_message(self.original)
        if self.message is None:
            print "Done!"
            self.quit()
        else:
            self.message, self.original, image = self.message
            print "Loading image"
            self.dataimage = Image.open(image)
            self.image = ImageTk.PhotoImage(self.dataimage)
            self.panel.configure(image=self.image)
            
        

    def has_tree(self, event):
        print event.x, event.y 
        ratio = 16
        pixel = self.dataimage.resize( [s/ratio for s in self.dataimage.size], Image.ANTIALIAS ).getpixel((event.x/ratio, event.y/ratio))
        pixel = [p / 256.0 for p in pixel]
        print pixel
        hue = rgb_to_hsv(*pixel)
        print hue
        hue = hue[0]
        hue = ((int(hue * 360.0 + 355 ) % 360) / 10 ) * 10
        
        print "Has tree"
        datum = {'tree': '%d %d' % (event.x, event.y),
                 'treehue': hue}
        self.next(datum)
        
    def has_notree(self, event=None):
        print "Has no tree"
        datum = {'tree': ''}
        self.next(datum)

    def createWidgets(self):

        self.panel = tk.Label(self)
        self.panel.grid()

        self.panel.focus()

        self.notree = tk.Button(self, text='No Tree',
                                 command=self.has_notree)
        self.notree.grid()

        self.quitButton = tk.Button(self, text='Quit',
                                    command=self.quit)            
        self.quitButton.grid()            
        self.bind("<Key>", self.has_notree)
        self.panel.bind("<Key>", self.has_notree)
        self.panel.bind("<Button-1>", self.has_tree)

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

    app = Application()                       
    app.master.title('Sample application')    
    app.mainloop()                     
