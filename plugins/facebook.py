import datetime
import json
import re
import time
import urllib2
from celery.task import task,TaskSet
from celery.result import AsyncResult
from utils import cache
import settings


@task        
def facebook(query, refresh_url=None, **kwargs):
        logger = facebook.get_logger(**kwargs)
        if refresh_url:
            url = refresh_url
        else:
            url = "https://graph.facebook.com/search?q=%s&type=post&limit=25&access_token=%s" % (query.replace('_','%20'),settings.FACEBOOK_API_KEY)
        try:
            data = json.loads(urllib2.urlopen(url).read())
            items = data['data']
            if data.get('paging'):
                refresh_url = data['paging']['previous']
            else:
                refresh_url = url
            return refresh_url,TaskSet(facebook_post.subtask((item,query, )) for item in items).apply_async()
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
            "query": query,
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
        return post_info

# vim: ai ts=4 sts=4 et sw=4
