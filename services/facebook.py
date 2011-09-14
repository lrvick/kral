import re
import datetime
import settings
from utils import fetch_json
from celery.task import task,TaskSet


@task
def feed(query, refresh_url=None, **kwargs):
    logger = feed.get_logger()
    if refresh_url:
        url = refresh_url
    else:
        url = "https://graph.facebook.com/search?q=%s&type=post&limit=25&access_token=%s"
        url = url % (query.replace('_','%20'),settings.FACEBOOK_API_KEY)
    data = fetch_json('facebook',logger,url)
    if data:
        items = data['data']
        if data.get('paging'):
            refresh_url = data['paging']['previous']
        else:
            refresh_url = url
        taskset = TaskSet(post.subtask((item,query, )) for item in items).apply_async()
        for result in taskset.results:
            result.task_name = None
        return refresh_url,taskset


@task
def post(item, query, **kwargs):
    logger = post.get_logger()
    if 'message' in item:
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
            "date": str(datetime.datetime.strptime(item['created_time'], settings.TIME_FORMAT)),
        }
        url_regex = re.compile('(?:http|https|ftp):\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
        for url in url_regex.findall(item['message']):
            post_info['links'].append({ 'href' : url })
        post_info['user']['avatar'] = "http://graph.facebook.com/%s/picture" % item['from']['id']
        if 'to' in item:
            post_info['to_users'] = item['to']['data']
        if 'likes' in item:
            post_info['likes'] = item['likes']['count']
        if 'application' in item and item['application'] is not None:
                post_info['application'] = item['application']['name']
        return post_info

# vim: ai ts=4 sts=4 et sw=4
