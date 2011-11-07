import base64
import time
import simplejson as json
from eventlet.green import urllib2
import urllib

def stream(queries, queue, settings):
    url = 'https://stream.twitter.com/1/statuses/filter.json'
    
    queries = [q.lower() for q in queries]
    quoted_queries = [urllib.quote(q) for q in queries]

    query_post = 'track=' + ",".join(quoted_queries)        

    request = urllib2.Request(url, query_post)
    
    auth = base64.b64encode('%s:%s' % (settings.get('Twitter','user'), settings.get('Twitter','pass')))
    
    request.add_header('Authorization', "basic %s" % auth)
    
    for item in urllib2.urlopen(request):
        try:
            item = json.loads(item)
        except json.JSONDecodeError:
            continue

        if 'text' in item and 'user' in item:
            
            #make sure the query is in the text
            #differntiate between what query is being currently searched
            for query_str in queries:
                if query_str in item['text'].lower():
                    query = query_str
                else:
                    query = None

            lang = False
            settings_lang = settings.get("Twitter", 'lang')
            if settings_lang:
                if item['user']['lang'] == settings_lang:
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
                    'text' : item['text'],
                    'query' : query,
                    'geo' : item['coordinates'],
                }
                for url in item['entities']['urls']:
                    post['links'].append({ 'href' : url.get('url') })
                queue.put(post)

