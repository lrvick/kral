import json
import time
import urllib2
from celery.task import Task
from kral.models import Query
from kral.tasks import *
from kral.views import push_data
from django.conf import settings


class Flickr(Task):
    """
    Initialize the Flickr Kral plugin.
    
    Keyword arguments:
    queries -- A dict of queries to search
    
    Returns nothing.
    """
    def run(self, querys, abort=False, **kwargs):
        for query in querys:
            FlickrFeed.delay(query)

class FlickrFeed(Task):
    def run(self,query,top_id_seen='0',**kwargs):
        logger = self.get_logger(**kwargs)
        url = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=%s&tags=%s&format=json&nojsoncallback=1" % FLICKR_API_KEY, query
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return e
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_querys = Query.objects.order_by('last_processed')[:slots]
        if query in all_querys:
            if top_id_seen is not '0':
                time.sleep(10)
            FlickrFeed.delay(query,top_id_seen)
            try:
                # What follows is an...inelegant solution for Flickr.
                # Especially for branding and such, we would do well to collect
                # tags that are placed after the initial upload. People may tag
                # a coke much later than the initial upload, for instance,
                # because they're a coke fan, whereas the original uploader
                # doesn't care.. I'm not sure how we could balance this with
                # the other plugins, though, or how that could be done without
                # Flickr adding something else to their API.
                for photo in data['photos']['photo']:
                    # Only process new photos
                    if int(photo['id']) > top_id_seen: 
                        ProcessFLPhoto.delay(item,query)
                        return "Spawned Processors"
                        # Keep track of the most recent we've seen this loop
                        if int(photo['id']) > top_session_id: 
                            top_session_id = int(photo['id'])
                    # And update our latest
                    if top_session_id > top_id_seen: 
                        top_id_seen = top_session_id

                    return "No updates"
            except:
                return "No data"
        else:
            return "Exiting Feed"
   
class ProcessFLPhoto(Task):
    def run(self, item, query, **kwargs):
        logger = self.get_logger(**kwargs)
        item['url'] = "http://flickr.com/" + item['owner'] + "/" + item['id']
        item['thumbnail'] = "http://farm" \
                            + item['farm'] \
                            + ".static.flickr.com/" \
                            + item['server'] \
                            + "/" \
                            + item['id'] \
                            + "_" \
                            + item['secret'] \
                            + "_s.jpg"
        post_info = {
                "service" : 'flickr',
                "id" : item['id'],
                "date" : time.time(),
                "user" : { "id" = item['owner'], },
                "source" : item['url'],
                "text" : item["title"],
                "thumbnail" : item['thumbnail'],
        }
        post_data(post_info)
        return "Saved Post/User"

# vim: ai ts=4 sts=4 et sw=4
