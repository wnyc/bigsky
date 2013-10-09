import flickrapi
import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('flickr_key', None, 'Flickr API Key')
gflags.DEFINE_string('flickr_secret', None, 'Flickr API secret')


# Poor man's memoizastion :-/ 
_flickr_api_cache = None

def flickr_api():
    global _flickr_api_cache
    if _flickr_api_cache is None:
        _flickr_api_cache = flickrapi.FlickrAPI(FLAGS.flickr_key, secret=FLAGS.flickr_secret)
    return _flickr_api_cache


class Photo:
    def __init__(self, photo_xml):
        attrs = photo_xml.attrib
        self.attrs = attrs

    def __repr__(self):
        return repr(self.attrs)



def get_photos(**kwargs):
    import urllib2
    while True:
        try:
            photos = flickr_api().photos_search(media='photos', 
                                                extras='date_taken, geo, url_o, url_z, url_t, url_s, tags', **kwargs)
            break
        except urllib2.HTTPError:
            print "Trying again"
    print photos.items()
    photos = photos.find('photos')
    photos = photos.findall('photo')
    photos = list(photos)
    print len(photos)
    for photo in photos:
        photo = photo.attrib
        yield photo
