from eventlet.greenthread import sleep
from eventlet.green import urllib2
import simplejson as json
import urllib
from collections import defaultdict

#NOTE: look into "dupe-protection" by using the start-index and max-results parameters

def stream(queries, queue, settings):
    api_url = "http://gdata.youtube.com/feeds/api/videos?"
   

    prev_ids = defaultdict(list) #keep a rolling list of the last previous ids 
                                 #to avoid dupes

    while True:
        
        for query in queries:

            p = {
                'q':query,
                'orderby': settings.get('Youtube', 'orderby', 'published'),
                'max-results': settings.get('Youtube', 'maxresults', 25), 
                'v': 2, 
                'alt': 'json',
            }    
            
            url  =  api_url + urllib.urlencode(p)

            request = urllib2.Request(url)
            
            response = json.loads(urllib2.urlopen(request).read())
           
            if 'feed' in response and 'entry' in response['feed']:
                
                entries = response['feed']['entry']

                for entry in entries:
                    
                    entry_id =  entry['media$group']['yt$videoid']['$t']
                    
                    if entry_id not in prev_ids[query]: #if we've already seen this id skip it

                        post = {
                            "service"     : "youtube",
                            "id"          : entry_id, 
                            "query"       : query,
                            "date"        : entry['media$group']['yt$uploaded']['$t'],
                            "user"        : {
                                                "name"    : entry['author'][0]['name']['$t'],
                                                "profile" : entry['author'][0]['uri']['$t'],
                                            },
                            "source"      : entry['media$group']['media$player']['url'],
                            "text"        : entry['media$group']['media$title']['$t'],
                            "description" : entry['media$group']['media$description'].get('$t', ''),
                            "keywords"    : entry['media$group']['media$keywords'].get('$t', ''),
                            "duration"    : entry['media$group']['yt$duration']['seconds'], 
                        }
                        
                        if 'yt$statistics' in entry:
                            post['favorites'] = entry['yt$statistics'].get('favoriteCount', 0)
                            post['views'] = entry['yt$statistics'].get('viewCount', 0)
                        if 'yt$rating' in entry:
                            post['likes'] = entry['yt$statistics'].get('numLikes', 0)
                            post['dislikes'] = entry['yt$statistics'].get('numDislikes', 0)

                        prev_ids[query].insert(0, post['id']) #add the entry ids to previous ids for query

                        queue.put(post)
            
            #use the size of double max results as the buffer for dupes
            prev_ids[query] = prev_ids[query][:int(settings.get('Youtube', 'maxresults', 25)) * 3] 
            
            sleep(5)



