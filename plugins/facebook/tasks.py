import datetime
import json
import re
import time
import urllib2
from celery.decorators import periodic_task,task
from celery.result import AsyncResult
from django.conf import settings
from kral.views import push_data, fetch_queries

try:
    import redis
    cache = redis.Redis(host='localhost', port=6379, db=0)
except ImportError:
    redis = False
    from django.core.cache import cache

@periodic_task(run_every = getattr(settings, 'KRAL_WAIT', 5))
def run(**kwargs):
    queries = fetch_queries()
    for query in queries:
        cache_name = "facebookfeed_%s" % query
        if cache.get(cache_name):
            previous_result = AsyncResult(cache.get(cache_name))
            if previous_result.ready():
                result = facebook_feed.delay(query)
                cache.set(cache_name,result.task_id)
        else:
            result = facebook_feed.delay(query)
            cache.set(cache_name,result.task_id)
            return

@task        
def facebook_feed(query, **kwargs):
    logger = facebook_feed.get_logger(**kwargs)
    cache_name = "facebook_prevurl_%s" % query
    if cache.get(cache_name):
        url = cache.get(cache_name)
    else:
        url = "https://graph.facebook.com/search?q=%s&type=post&limit=25&access_token=%s" % (query.replace('_','%20'),settings.FACEBOOK_API_KEY)
    try:
        data = json.loads(urllib2.urlopen(url).read())
        items = data['data']
        if data.get('paging'):
            prev_url = data['paging']['previous']
        else:
            prev_url = url
        for item in items:
            facebook_post.delay(item, query)
        cache.set(cache_name,str(prev_url))
        return
    except urllib2.HTTPError, error:
        logger.error("Facebook API returned HTTP Error: %s - %s" % (error.code,url))
    except urllib2.URLError, error:
        logger.error("Facebook API returned URL Error: %s - %s" % (error,url))
   
@task
def facebook_post(item, query, **kwargs):
    logger = facebook_post.get_logger(**kwargs)
    time_format = "%Y-%m-%dT%H:%M:%S+0000"
    if item.has_key('message'):
        post_info = {
            "service" : 'facebook',
            "user" : {
                "name": item['from'].get('name'),
                "id": item['from']['id'],
            },
            "links" : [],
            "id" : item['id'],
            "text" : item['message'],
            "date": str(datetime.datetime.strptime(item['created_time'], time_format)),
        }
        url_regex = re.compile('(?:http|https|ftp):\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
        for url in url_regex.findall(item['message']):
            post_info['links'].append({ 'href' : url })
        post_info['user']['avatar'] = "http://graph.facebook.com/%s/picture" % item['from']['id']
        if item.get('to'):
            post_info['to_users'] = item['to']['data']
        if item.get('likes'):
            post_info['likes'] = item['likes']['count']
        if item.get('application'):
            post_info['application'] = item['application']['name']
        push_data(post_info, queue=query)
        return

# vim: ai ts=4 sts=4 et sw=4
