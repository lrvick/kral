import json
import time
import urllib2
from celery.task import Task
from kral.models import Query
from kral.tasks import *
from kral.views import push_data
from django.conf import settings


class Flickr(Task):
    def run(self, queries, abort=False, **kwargs):
        """Initialize the Flickr Kral plugin.
        
        Keyword arguments:
        queries -- A dict of queries to search
        
        Returns nothing.

        """
        for query in queries:
            FlickrFeed.delay(query)


class FlickrFeed(Task):
    def run(self, query, top_id_seen=0, **kwargs):
        logger = self.get_logger(**kwargs)
        url = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=%s&tags=%s&format=json&nojsoncallback=1&extras=owner_name,geo,description,tags,date_upload" % (settings.FLICKR_API_KEY, query)
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return e
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_queries = Query.objects.order_by('last_processed')[:slots]
        if query in all_queries:
            if top_id_seen:
                logger.info("Sleeping for: %s | Query: %s" % (top_id_seen, query))
                time.sleep(10)
            #FlickrFeed.delay(query, top_id_seen)
            # What follows is an...inelegant solution for Flickr.
            # Especially for branding and such, we would do well to
            # collect tags that are placed after the initial upload.
            # People may tag a coke much later than the initial upload,
            # for instance, because they're a coke fan, whereas the
            # original uploader doesn't care.. I'm not sure how we could
            # balance this with the other plugins, though, or how that
            # could be done without Flickr adding something else to
            # their API.
            photos = data['photos']['photo']
            photo_ids = [int(p['id']) for p in photos]
            photo_ids.sort()
          
            if data['stat'] == "ok":
                for photo in data['photos']['photo']:
                    # Only process new photos
                    if int(photo['id']) > top_id_seen: 
                        ProcessFLPhoto.delay(photo, query)
                        logger.info("Spawned Flickr photo processor for query: %s" % query)
            else:
                raise Exception("Flickr API Error Code %s: %s" % (data['code'], data['message']))
            top_id_seen = photo_ids[-1]
            logger.info("Top id seen: %s | Query: %s" % (top_id_seen, query))
            FlickrFeed.delay(query, top_id_seen)
        else:
            logger.info("Exiting Feed")
   
class ProcessFLPhoto(Task):
    def run(self, photo_info, query, **kwargs):
        print(photo_info)
        logger = self.get_logger(**kwargs)
        #photo_info['url'] = "http://flickr.com/%s/%s" % (user_info['path_alias'], photo_info['id'])
        photo_info['thumbnail'] = "http://farm{farm}.static.flickr.com/{server}/{id}_{secret}_m.jpg".format(**photo_info)
        post_info = {
            "service" : 'flickr',
            "id" : photo_info['id'],
            "date" : photo_info['dateupload'],
            "user" : {
                "id" : photo_info['owner'],
                "name" : photo_info['ownername'],
                #"avatar" : "http://farm{iconfarm}.static.flickr.com/{iconserver}/buddyicons/{nsid}.jpg".format(**user_info),
                #"postings" : user_info['photos']['count'].get('_content', ""),
                #"profile" : user_info['profileurl'].get('_content', ""),
                #"website" : user_info['photosurl'].get('_content', ""),
            },
            "text" : photo_info["title"],
            "thumbnail" : photo_info['thumbnail'],
        }
        logger.info("Saved Post/User")
        push_data(post_info,queue=query)

# vim: ai ts=4 sts=4 et sw=4
