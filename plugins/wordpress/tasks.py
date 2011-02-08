import json,time,urllib,urllib2,datetime,rfc822,re
from xml.dom import minidom
from django.conf import settings
from django.core.cache import cache
from celery.decorators import periodic_task, task
from celery.result import AsyncResult
from kral.views import push_data, fetch_queries

@periodic_task(run_every = getattr(settings, 'KRAL_WAIT', 5))
def wordpress(**kwargs):
    queries = fetch_queries()
    for query in queries:
        cache_name = "wordpressfeed_%s" % query.replace('_','')
        if cache.get(cache_name): 
            previous_result = AsyncResult(cache.get(cache_name))
            if previous_result.ready():
                result = wordpress_feed.delay(query)
                cache.set(cache_name,result.task_id)
        else:
            result = wordpress_feed.delay(query)
            cache.set(cache_name,result.task_id)

@task
def wordpress_feed(query, **kwargs):
    logger = wordpress_feed.get_logger(**kwargs)
    fetch_method = getattr(settings, 'WORDPRESS_FETCHMETHOD', 'rss')
    cache_name = "wordpressfeed_lastid_%s" % query.replace('_','')
    last_seen = cache.get(cache_name,None)
    try:
        if fetch_method == 'json':
            url = "http://en.search.wordpress.com/?q=%s&s=date&f=json" % query.replace(' ','')
            posts = json.loads(urllib2.urlopen(url).read())
        elif fetch_method == 'rss':
            url = "http://en.wordpress.com/tag/%s/feed/" % query.replace(' ','')
            try:
                posts = minidom.parse(urllib2.urlopen(url)).getElementsByTagName("item")
            except:
                posts = None
    except urllib2.HTTPError, error:
        logger.error("Wordpress API returned HTTP Error: %s - %s" % (error.code,url))
        posts = None
    if posts:
        for post in posts:
            if fetch_method == 'json':
                epoch_time = post['epoch_time']
            elif fetch_method == 'rss':
                epoch_time = time.mktime(rfc822.parsedate(post.childNodes[5].firstChild.data))
            if post.childNodes[1].firstChild is not None and post.childNodes[13].firstChild is not None:
                if last_seen:
                    if int(epoch_time) > int(last_seen):
                        wordpress_entry.delay(post, query)
                        cache.set(cache_name,epoch_time)
                else:
                    wordpress_entry.delay(post, query)
                    cache.set(cache_name,epoch_time)

@task
def wordpress_entry(post, query, **kwargs):
    logger = wordpress_entry.get_logger(**kwargs)
    fetch_method = getattr(settings, 'WORDPRESS_FETCHMETHOD', 'rss')
    default_avatar = getattr(settings, 'WORDPRESS_DEFAULTAVATAR', 'http://sabahkamal.files.wordpress.com/2007/04/wordpress-logo.thumbnail.jpg')
    author = post.childNodes[7].firstChild.data
    try:
        gravitar_json = json.loads(urllib2.urlopen('http://en.gravatar.com/%s.json' % author).read())
        avatar = "%s?%s" % (gravitar_json['entry'][0]['thumbnailUrl'],urllib.urlencode({'d':default_avatar,'s':'48'}))
    except Exception, e :
        avatar = default_avatar
    if fetch_method == 'json':
        post_info = {
            "service" : 'wordpress',
            "date": post['epoch_time'],
            "user": {
                "name":post['author'],
                "avatar":avatar,
            },
            "text":post['content'],
            "source":post['guid'],
        }
    elif fetch_method == 'rss':
        post_info = {
            "service" : 'wordpress',
            "date": str(datetime.datetime.fromtimestamp(rfc822.mktime_tz(rfc822.parsedate_tz(post.childNodes[5].firstChild.data)))),
            "user": {
                "name":author,
                "avatar":avatar,
            },
            "text": post.childNodes[1].firstChild.data,
            "description": re.sub(r'<[^>]*?>', '', post.childNodes[13].firstChild.data),
            "source": post.childNodes[3].firstChild.data,
        }
    push_data(post_info, queue=query)
    logger.info("Pushed Wordpress Post data.")

# vim: ai ts=4 sts=4 et sw=4
