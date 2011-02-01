import json,time,urllib2,pickle
from django.conf import settings
from django.core.cache import cache
from celery.task import Task
from celery.result import AsyncResult
from kral.tasks import *
from kral.models import Query
from kral.views import push_data

class Flickr(PeriodicTask):
    run_every = getattr(settings, 'KRAL_WAIT', 5)
    def run(self, **kwargs):
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        queries = Query.objects.order_by('last_processed')[:slots]
        if cache.get('flickr_tasks'):
            flickr_tasks = pickle.loads(cache.get('flickr_tasks'))
        else:
            flickr_tasks = {}
        for query in queries:
            try:
                previous_result = AsyncResult(flickr_tasks[str(query)])
                if previous_result.ready():
                    result = FlickrFeed.delay(query)
                    flickr_tasks[str(query)] = str(result.task_id)
            except:
                result = FlickrFeed.delay(query)
                flickr_tasks[str(query)] = str(result.task_id)
        cache.set('flickr_tasks',pickle.dumps(flickr_tasks))
       
class FlickrFeed(Task):
    def run(self, query, **kwargs):
        logger = self.get_logger(**kwargs)
        url = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=%s&tags=%s&format=json&nojsoncallback=1&per_page=50&extras=owner_name,geo,description,tags,date_upload" % (settings.FLICKR_API_KEY, query)
        cache_name = "flickr_topid_%s" % query
        if cache.get(cache_name):
            top_id_seen = cache.get(cache_name)
        else:
            top_id_seen = 0
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return e
        photos = data['photos']['photo']
        photo_ids = [int(p['id']) for p in photos]
        photo_ids.sort()
        if data['stat'] == "ok":
            for photo in data['photos']['photo']:
                if int(photo['id']) > top_id_seen: 
                    ProcessFLPhoto.delay(photo, query)
                    logger.info("Spawned Flickr photo processor for query: %s" % query)
            top_id_seen = photo_ids[-1]
            cache.set(cache_name,str(top_id_seen))
            logger.info("Top id seen: %s | Query: %s" % (top_id_seen, query))
            return True
        else:
            raise Exception("Flickr API Error Code %s: %s" % (data['code'], data['message']))
   
class ProcessFLPhoto(Task):
    def run(self, photo_info, query, **kwargs):
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
