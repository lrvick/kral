import datetime
import json
import time
import urllib2
from celery.decorators import periodic_task, task
from celery.result import AsyncResult

from kral.utils import cache, push_data, fetch_queries 
from kral import settings

@periodic_task(run_every = getattr(settings, 'KRAL_WAIT', 5))
def buzz(**kwargs):
    queries = fetch_queries()
    for query in queries:
        cache_name = "buzzfeed_%s" % query.replace(' ','').replace('_','')
        if cache.get(cache_name): 
            previous_result = AsyncResult(cache.get(cache_name))
            if previous_result.ready():
                result = buzz_feed.delay(query)
                cache.set(cache_name,result.task_id)
        else:
            result = buzz_feed.delay(query)
            cache.set(cache_name,result.task_id)

@task
def buzz_feed(query,**kwargs):
    logger = buzz_feed.get_logger(**kwargs)
    time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    url = "http://www.googleapis.com/buzz/v1/activities/search?alt=json&orderby=published&q=%s&key=%s" % (query.replace('_',''),settings.BUZZ_API_KEY)
    cache_name = "buzzfeed_prevdate_%s" % query
    prev_date = cache.get(cache_name)
    if prev_date == None:
        prev_date = 0
    try:
        data = json.loads(urllib2.urlopen(url).read())
    except urllib2.HTTPError, error:
        data = None
        logger.error("Buzz API returned HTTP Error: %s - %s" % (error.code,url))
    if data:
        if data['data'].get('items',None):
            for item in data['data']['items']:
                if item.get('updated'):
                    this_date = int(time.mktime(time.strptime(item['updated'],time_format)))
                    if int(this_date) > int(prev_date):
                        buzz_post.delay(item,query)
                        cache.set(cache_name,this_date)

@task
def buzz_post(item, query, **kwargs):
    logger = buzz_post.get_logger(**kwargs)
    time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    # FIXME should consider all pictures, not just one
    try: 
        thumbnail = item['object']['attachments'][0]['links']['preview'][0]['href']
        picture = item['object']['attachments'][0]['links']['enclosure'][0]['href']
    except:
        picture = ""
        thumbnail = ""
    # END FIXME
    post_info = {
            "service" : 'buzz',
            "user" : {
                "name" : item['actor']['name'],
                "id" : item['actor']['name'],
                "avatar": item['actor']['thumbnailUrl'],
                "source": item['actor']['profileUrl'], 
            },
            "pictures" : { # hard-coding for only one picture. See above FIXME
                "0": {
                    "picture": picture,
                    "thumbnail": thumbnail,
                },
            },
            "id" : item['id'].split(":")[3],
            "date" : str(datetime.datetime.strptime(item['published'],time_format)),
            "source" : item['object']['links']['alternate'][0]['href'],
            "text" : item["object"]['content'],
    }
    push_data(post_info, queue = query)
    logger.info("Saved Post/User")

# vim: ai ts=4 sts=4 et sw=4
