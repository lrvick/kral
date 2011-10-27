from eventlet.greenthread import sleep
from eventlet.green import urllib2
import simplejson as json
import urllib

def stream(queries, queue, config):
    api_url = "http://gdata.youtube.com/feeds/api/videos?"

    while True:
        for query in queries:
            
            p = {
                'q':query,
                'orderby': 'published',
                'max-results': 25, 
                'v': 2, 
                'alt': 'json',
            }    
            
            url  =  api_url + urllib.urlencode(p)

            request = urllib2.Request(url)
            
            response = json.loads(urllib2.urlopen(request).read())
            
            if 'feed' in response and 'entry' in response['feed']:
                
                entries = response['feed']['entry']

                for entry in entries:
                    
                    post = {
                        "service": "youtube",
                        "id"          : entry['media$group']['yt$videoid']['$t'],
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

                    queue.put(post)
        
                    sleep(1)

