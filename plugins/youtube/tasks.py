import urllib2,json,time,datetime,pickle
from django.conf import settings
from django.core.cache import cache
from celery.decorators import periodic_task, task
from celery.result import AsyncResult
from kral.views import push_data, fetch_queries

@periodic_task(run_every = getattr(settings, 'KRAL_WAIT', 5))
def youtube(**kwargs):
    queries = fetch_queries()
    for query in queries:
        cache_name = "youtubefeed_%s" % query.replace(' ','').replace('_','')
        if cache.get(cache_name): 
            previous_result = AsyncResult(cache.get(cache_name))
            if previous_result.ready():
                result = youtube_feed.delay(query)
                cache.set(cache_name,result.task_id)
        else:
            result = youtube_feed.delay(query)
            cache.set(cache_name,result.task_id)
@task
def youtube_feed(query, **kwargs):
    logger = youtube_feed.get_logger(**kwargs)
    url = "http://gdata.youtube.com/feeds/api/videos?q=%s&orderby=published&max-results=25&v=2&alt=json" % query.replace('_','')
    cache_name = "youtubefeed_prevlist_%s" % query
    try:
        prev_list = pickle.loads(cache.get(cache_name))
    except Exception:
        prev_list = []
    try:
        data = json.loads(urllib2.urlopen(url).read())
    except urllib2.HTTPError, error:
        logger.error("Youtube API returned HTTP Error: %s - %s" % (error.code,url))
        data = None
    if data:
        if data['feed'].get('entry'):
            entries = data['feed']['entry']
            id_list = [e['id']['$t'].split(':')[-1] for e in entries]
            try:
                for entry in entries: 
                    v_id = entry['id']['$t'].split(':')[-1]
                    if v_id in prev_list:
                        pass
                    else:
                        youtube_video.delay(entry, query)
                        prev_list.append(v_id)
                        prev_list = prev_list[:50]
                        cache.set(cache_name,pickle.dumps(prev_list))
                    logger.info("Spawned Processors")
            except Exception, e:
                raise e
   
@task
def youtube_video(item, query, **kwargs):
    logger = youtube_video.get_logger(**kwargs)
    if item.has_key('title'):
        post_info = {
                "service" : 'youtube',
                "id" : item['media$group']['yt$videoid']['$t'],
                "date" : item['media$group']['yt$uploaded']['$t'],
                "user" : item['author'][0]["name"]['$t'],
                "source" : item['link'][1]['href'],
                "text" : item["title"]['$t'],
                "keywords" : item['media$group']['media$keywords'].get('$t',''),
                "description" : item['media$group']['media$description']['$t'],
                "thumbnail" : "http://i.ytimg.com/vi/%s/hqdefault.jpg" % item['media$group']['yt$videoid']['$t'],
                "duration" : item['media$group']['yt$duration']['seconds'],
        }
        push_data(post_info, queue = query)
    logger.info("Saved Post/User")

# vim: ai ts=4 sts=4 et sw=4
