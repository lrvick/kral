from eventlet.greenthread import sleep
from eventlet.green import urllib2
import simplejson as json
import urllib
from collections import defaultdict

#TODO: look into using the start-index and max-results parameters

def stream(queries, queue, settings):

    mode = settings.get('Youtube', 'mode', 'most_popular')

    api_url = "http://gdata.youtube.com/feeds/api/standardfeeds/%s?" % mode 

    prev_ids = defaultdict(list)

    while True:
        
        for query in queries:

            p = {
                'q': query,
                'orderby': settings.get('Youtube', 'orderby', 'published'),
                'max-results': settings.get('Youtube', 'maxresults', 25), 
                'v': 2, 
                'alt': 'jsonc',
                'format': 5,
            }    

            #time is only supported in these standard video feeds
            if mode in ['top_rated', 'top_favorites', 'most_viewed', 
                    'most_popular', 'most_discussed', 'most_responded',]:
                p['time'] = settings.get('Youtube', 'time', 'today')

            url  =  api_url + urllib.urlencode(p)
            
            request = urllib2.Request(url)
            
            response = json.loads(urllib2.urlopen(request).read())
           
            if 'data' in response and 'items' in response['data']:
                
                entries = response['data']['items']
                
                for entry in entries:

                    #['uploaded',
                    #'category', 
                    #'updated',
                    #'rating',
                    #'description',
                    #'title',
                    #'tags',
                    #'thumbnail',
                    #'content', 
                    #'player',
                    #'accessControl',
                    #'uploader',
                    #'ratingCount',
                    #'duration',
                    #'aspectRatio', 
                    #'likeCount',
                    #'favoriteCount',
                    #'id', 
                    #'viewCount']
                    
                    entry_id =  entry['id']
                    
                    uploader = entry['uploader']

                    profile_url = "http://youtube.com/" + uploader

                    if entry_id not in prev_ids[query]: #if we've already seen this id skip it

                        post = {
                            "service"     : "youtube",
                            "id"          : entry_id, 
                            "query"       : query,
                            "date"        : entry['uploaded'],
                            "user"        : {
                                                "name"    : uploader,
                                                "profile" : profile_url,
                                            },
                            "source"      : entry['player']['default'],
                            "text"        : entry['title'],
                            "description" : entry.get('description', ''),
                            "category"    : entry['category'],
                            "keywords"    : entry.get('tags', ''),
                            "duration"    : entry['duration'], 
                            'favorites'   : entry.get('favoriteCount', 0),
                            'views'       : entry.get('viewCount', 0),
                            'likes'       : entry.get('likeCount', 0),
                            #'dislikes'    : entry.get('numDislikes', 0), -- isn't made available?
                        }

                        prev_ids[query].insert(0, entry_id) #add the entry ids to previous ids for query

                        queue.put(post)
                
            #use 50 item buffer for dupes
            #TODO: look into deque
            prev_ids[query] = prev_ids[query][:50] 
            
            sleep(15)



