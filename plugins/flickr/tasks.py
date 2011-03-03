import json,time,urllib2,httplib,pickle,redis
from django.conf import settings
from django.core.cache import cache
from celery.decorators import periodic_task, task
from celery.result import AsyncResult
from kral.views import push_data, fetch_queries

cache = redis.Redis()

@periodic_task(run_every = getattr(settings, 'KRAL_WAIT', 5))
def flickr(**kwargs):
    queries = fetch_queries()
    for query in queries:
        cache_name = "flickrfeed_%s" % query.replace(' ','').replace('_','')
        if cache.get(cache_name): 
            previous_result = AsyncResult(cache.get(cache_name))
            if previous_result.ready():
                result = flickr_feed.delay(query)
                cache.set(cache_name,result.task_id)
        else:
            result = flickr_feed.delay(query)
            cache.set(cache_name,result.task_id)
 
@task
def flickr_feed(query, **kwargs):
    logger = flickr_feed.get_logger(**kwargs)
    url = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=%s&tags=%s&format=json&nojsoncallback=1&per_page=50&extras=owner_name,geo,description,tags,date_upload" % (settings.FLICKR_API_KEY, query.replace('_','+'))
    cache_name = "flickrtopid_%s" % query.replace(' ','').replace('_','')
    top_id_seen = cache.get(cache_name) or 0          
    photos = None
    try:
        data = json.loads(urllib2.urlopen(url).read())
        photos_data = data.get('photos')
        if photos_data:
            photos = photos_data['photo']
    except ValueError: 
        pass
    except urllib2.HTTPError, error:
        logger.error("Flickr API returned HTTP Error: %s - %s" % (error.code,url))
    except urllib2.URLError, error:
        logger.error("Flickr API returned URL Error: %s - %s" % (error,url))
    except httplib.BadStatusLine, error:
        logger.error("Flickr API returned a bad status line: %s" % (error))
    if photos:
        photo_ids = [int(p['id']) for p in photos]
        photo_ids.sort()
        if data['stat'] == "ok": 
            for photo in photos:
                if int(photo['id']) > int(top_id_seen):
                    flickr_photo.delay(photo, query)
                    logger.info("Spawned Flickr photo processor for query: %s" % query)
            top_id_seen = photo_ids[-1]
            cache.set(cache_name,str(top_id_seen))
            logger.info("Top id seen: %s | Query: %s" % (top_id_seen, query))
        else:
            raise Exception("Flickr API Error Code %s: %s" % (data['code'], data['message']))
   
@task
def flickr_photo(photo_info, query, **kwargs):
    logger = flickr_photo.get_logger(**kwargs)
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
