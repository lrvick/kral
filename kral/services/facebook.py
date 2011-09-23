import time
import re
import datetime
from kral.utils import fetch_json

def setup():
    print "running setup for facebook"
    pass

def stream(queries, queue, settings):
    while True:
        for query in queries:
            time.sleep(1)
            url = "https://graph.facebook.com/search?q=%s&type=post&limit=25&access_token=%s"
            url = url % (query,settings['FACEBOOK_API_KEY'])
            data = fetch_json('facebook',url)
            if data:
                items = data['data']
                for item in items:
                    if 'message' in item:
                        post = {
                            "service" : 'facebook',
                            "query": query,
                            "user" : {
                                "name": item['from'].get('name'),
                                "id": item['from']['id'],
                            },
                            "links" : [],
                            "id" : item['id'],
                            "text" : item['message'],
                            "date": str(datetime.datetime.strptime(item['created_time'], settings['TIME_FORMAT'])),
                        }
                        url_regex = re.compile('(?:http|https|ftp):\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
                        for url in url_regex.findall(item['message']):
                            post['links'].append({ 'href' : url })
                        post['user']['avatar'] = "http://graph.facebook.com/%s/picture" % item['from']['id']
                        if 'to' in item:
                            post['to_users'] = item['to']['data']
                        if 'likes' in item:
                            post['likes'] = item['likes']['count']
                        queue.put(post)
