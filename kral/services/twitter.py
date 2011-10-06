import base64
import datetime
import simplejson as json
from eventlet.green import urllib2

def stream(queries, queue, settings):
    url = 'https://stream.twitter.com/1/statuses/filter.json'
    query_post = str("track="+",".join([q for q in queries]))
    httprequest = urllib2.Request(url,query_post)
    auth = base64.b64encode('%s:%s' % (settings.get('Twitter','user'), settings.get('Twitter','pass')))
    httprequest.add_header('Authorization', "basic %s" % auth)
    for item in urllib2.urlopen(httprequest):
        item = json.loads(item)
        if 'text' in item and 'user' in item:
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
                #'date' : str(datetime.datetime.strptime(item['created_at'], settings.get('Twitter','time_format')),
                'text' : item['text'],
                'geo' : item['coordinates'],
            }
            for url in item['entities']['urls']:
                post['links'].append({ 'href' : url.get('url') })
            queue.put(post)

