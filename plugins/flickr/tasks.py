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
        url = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=%s&tags=%s&format=json&nojsoncallback=1" % (settings.FLICKR_API_KEY, query)
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return e
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_queries = Query.objects.order_by('last_processed')[:slots]
        if query in all_queries:
            if top_id_seen is not '0':
                time.sleep(10)
            FlickrFeed.delay(query, top_id_seen)
            # What follows is an...inelegant solution for Flickr.
            # Especially for branding and such, we would do well to
            # collect tags that are placed after the initial upload.
            # People may tag a coke much later than the initial upload,
            # for instance, because they're a coke fan, whereas the
            # original uploader doesn't care.. I'm not sure how we could
            # balance this with the other plugins, though, or how that
            # could be done without Flickr adding something else to
            # their API.
            if data['stat'] == "ok":
                top_session_id = 0
                for photo in data['photos']['photo']:
                    # Only process new photos
                    if int(photo['id']) > top_id_seen: 
                        ProcessFLPhoto.delay(photo, query)
                        logger.info("Spawned Flickr photo processor for query: %s" % query)
                        if int(photo['id']) > top_session_id: 
                            top_session_id = int(photo['id'])
                    if top_session_id > top_id_seen: 
                        top_id_seen = top_session_id
            else:
                raise Exception("Flickr API Error Code %s: %s" % (data['code'], data['message']))
        else:
            logger.info("Exiting Feed")
   
class ProcessFLPhoto(Task):

    def run(self, photo_info, query, **kwargs):
        logger = self.get_logger(**kwargs)
        user_info = self.GetFLUsername(photo_info['owner'])
        user_info['path_alias'] = user_info.get('path_alias', "") #if path_alias in user_info else user_info['id']
        photo_info['url'] = "http://flickr.com/%s/%s" % (user_info['path_alias'], photo_info['id'])
        photo_info['thumbnail'] = "http://farm{farm}.static.flickr.com/{server}/{id}_{secret}_s.jpg".format(**photo_info)
        post_info = {
            "service" : 'flickr',
            "id" : photo_info['id'],
            "date" : time.time(),
            "user" : {
                "id" : user_info.get('nsid', ""),
                "avatar" : "http://farm{iconfarm}.static.flickr.com/{iconserver}/buddyicons/{nsid}.jpg".format(**user_info),
                "postings" : user_info['photos']['count'].get('_content', ""),
                "profile" : user_info['profileurl'].get('_content', ""),
                "website" : user_info['photosurl'].get('_content', ""),
            },
            "source" : photo_info['url'],
            "text" : photo_info["title"],
            "thumbnail" : photo_info['thumbnail'],
        }
        if user_info.get('name'):
            post_info['user']['name'] = user_info.get['username'].get('_content', "")
        if user_info.get('realname'):
            post_info['user']['real_name'] = user_info.get['realname'].get('_content', "")
        if user_info.get('location'):
            post_info['user']['location'] = user_info['location'].get('_content', "")
        print(post_info)
        push_data(post_info, query)
        logger.info("Saved Post/User")

    def GetFLUsername(self, user_id):
        """Given an nsid, return an array of user info"""
        url = "http://api.flickr.com/services/rest/?method=flickr.people.getinfo&api_key=%s&user_id=%s&format=json&nojsoncallback=1" % (settings.FLICKR_API_KEY, user_id)
        try:
            user_info = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return e
        if user_info['stat'] != "ok":
            raise Exception("FLICKR: Failed to retrieve user info: [%s] %s" % (data['code'], data['message']))
        else:
            return user_info['person']


# vim: ai ts=4 sts=4 et sw=4
