import base64
import time
import simplejson as json
from eventlet.green import urllib2

def stream(queries, queue, settings):
    url = 'https://stream.twitter.com/1/statuses/filter.json'
    queries = [q.lower() for q in queries]
    query_post = str("track="+",".join(queries))
    httprequest = urllib2.Request(url,query_post)
    auth = base64.b64encode('%s:%s' % (settings.get('Twitter','user'), settings.get('Twitter','pass')))
    httprequest.add_header('Authorization', "basic %s" % auth)
    for item in urllib2.urlopen(httprequest):
        try:
            item = json.loads(item)
        except json.JSONDecodeError:
            item = None
        if 'user' in item:
            if 'text' in item and 'user' in item:
                for query_str in queries:
                    if query_str in item['text'].lower():
                        query = query_str
            if query:
                post = {
                    'service' : 'twitter',
                    'user' : {
                        'id' : item['user']['id_str'],
                        'utc' : item['user']['utc_offset'],
                        'name' : item['user']['screen_name'],
                        'description' : item['user']['description'],
                        'location' : item['user']['location'],
                        'avatar' : item['user']['profile_image_url'],
                        'subscribers': item['user']['followers_count'],
                        'subscriptions': item['user']['friends_count'],
                        'website': item['user']['url'],
                        'language' : item['user']['lang'],
                    },
                    'links' : [],
                    'id' : item['id'],
                    'application': item['source'],
                    'date' : int(time.mktime(time.strptime(item['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))),
                    'text' : item['text'],
                    'query' : query,
                    'geo' : item['coordinates'],
                }
                for url in item['entities']['urls']:
                    post['links'].append({ 'href' : url.get('url') })
                queue.put(post)

