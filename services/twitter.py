import re
import json
import base64
import rfc822
import urllib2
import datetime
import settings
from utils import fetch_json
from celery.task import task,TaskSet

@task
def feed(query, url=None, **kwargs):
    logger = feed.get_logger()
    if not url:
        url = "http://search.twitter.com/search.json?q=%s&" % query
    data = fetch_json('twitter',logger,url)
    if data:
        items = data['results']
        print items[0]
        since_id = None # set since_id
        next_url = 'http://search.twitter.com/search.json?q=%s&since_id=%s' % (query,since_id)
        return next_url,TaskSet(post.subtask((item,query, )) for item in items).apply_async()

@task
def post(item, query, **kwargs):
    if item.has_key('text'):
        post_info = {
            "service" : 'twitter',
            "user" : {
                "name": item['from_user'],
                "id": item['from_user_id_str'],
                'avatar' : item['profile_image_url'],
            },
            "links" : [],
            "id" : item['id_str'],
            "text" : item['text'],
            "source": item['source'],
            "date": str(datetime.datetime.fromtimestamp(rfc822.mktime_tz(rfc822.parsedate_tz(item['created_at'])))),
        }
        url_regex = re.compile('(?:http|https|ftp):\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
        for url in url_regex.findall(item['text']):
            post_info['links'].append({ 'href' : url })
        return post_info

#vim: ai ts=5 sts=4 et sw=4
