# -*- coding: utf-8 -*-
import base64
import time
import simplejson as json
from eventlet.green import urllib2
import urllib
from kral import config

def stream(queries, queue, kral_start_time):

    url = 'https://stream.twitter.com/1/statuses/filter.json'

    queries = [q.lower() for q in queries]

    quoted_queries = [urllib.quote(q) for q in queries]

    query_post = 'track=' + ",".join(quoted_queries)

    request = urllib2.Request(url, query_post)

    auth = base64.b64encode('%s:%s' % (config.TWITTER['user'], config.TWITTER['password']))

    request.add_header('Authorization', "basic %s" % auth)

    request.add_header('User-agent', config.USER_AGENT)

    for item in urllib2.urlopen(request):
        try:
            item = json.loads(item)
        except json.JSONDecodeError: #for whatever reason json reading twitters json sometimes raises this
            continue


        if 'text' in item and 'user' in item:

            #determine what query we're on if it exists in the text
            text = item['text'].lower()

            query = ''
            for q in queries:
                q_uni = unicode(q, 'utf-8')
                if q_uni in text:
                    query = q_uni

            lang = False
            if config.LANG:
                if item['user']['lang'] == config.LANG:
                    lang = True
            else:
                lang = True

            if query and lang:

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
                        'text' : text,
                        'query' : query,
                        'geo' : item['coordinates'],
                        }
                
                for url in item['entities']['urls']:
                    post['links'].append({ 'href' : url.get('url') })

                queue.put(post)

