# -*- coding: utf-8 -*-
import time
import re
import urllib
import simplejson as json
from eventlet.green import urllib2
from eventlet.greenthread import sleep
from kral.utils import fetch_json
import urlparse
from kral import config

def stream(queries, queue, kral_start_time):
   
    def get_access_token():

        url_args = {
            'client_id' : config.FACEBOOK['app_id'], 
            'client_secret' : config.FACEBOOK['app_secret'],
            'grant_type' : 'client_credentials'
        }
        url = 'https://graph.facebook.com/oauth/access_token?%s' % urllib.urlencode(url_args)

        access_token = urllib2.urlopen(url).read().split('=')[1]

        return access_token

    access_token = get_access_token()

    #keep a store of queries and their previous_url since values to ensure we are 
    #getting new items in our feed
    sinces = {}
   
    user_agent = config.USER_AGENT
    print user_agent
    
    while True:
        print "Starting facebook"        
        print queries
        for query in queries:
            
            #https://developers.facebook.com/docs/reference/api/batch/
            #do batch requests for facebook, currently limited to 20
            url_args = {
                'access_token' : access_token,
                'batch': [
                    {
                        'method': "GET",
                        'name' : "get-user-ids",
                        "relative_url": "search?q=%s&type=post&limit=20" % urllib.quote(query),
                        "omit_response_on_success": 0,
                    },
                    {
                        'method':'GET',
                        'relative_url':'/feed/?ids={result=get-user-ids:$.data.*.from.id}',
                    }
                ]
            }

            #if we have stored a "since" for this query and its newer than when we started
            #use that timestamp instead, else use the time we started
            if query in sinces and sinces[query] > kral_start_time:
                since = sinces[query]
            else:
                since = kral_start_time
    
            #set the since to retreive new posts
            url_args['batch'][0]['relative_url'] = "%s&since=%s" % (url_args['batch'][0]['relative_url'], since)

            url = 'https://graph.facebook.com'
            request = urllib2.Request(url)
            request.add_data(urllib.urlencode(url_args))
            
            if user_agent:
                request.add_header('User-agent', user_agent)

            response = fetch_json(request)
           
            if not response:
                sleep(5)
                break

            posts, profiles = response
            print 'Posts', posts
            print 'Profiles', profiles
            if posts and profiles:
                
                decoded_posts = json.loads(posts['body'])
                decoded_profiles = json.loads(profiles['body'])

                if not decoded_posts['data']:
                    sleep(2) #don't process anything if we have no data 
                    continue

                #get the since value from the previous url
                if 'paging' in decoded_posts and 'previous' in decoded_posts['paging']:
                    parsed_paging_data = urlparse.parse_qs(decoded_posts['paging']['previous'])
                    previous_since = int(parsed_paging_data['since'][0])
                    sinces[query] = previous_since

                items = decoded_posts['data']

                for item in items:
                   
                    created_time = int(time.mktime(time.strptime(item['created_time'],'%Y-%m-%dT%H:%M:%S+0000')))
                   
                    #only process if these posts are in fact new
                    if created_time >= since:

                        if 'message' in item:
                            
                            post = {
                                "service" : 'facebook',
                                "query": query,
                                "user" : {
                                    "name": item['from'].get('name'),
                                    "id": item['from']['id'],
                                    "subscribers" : '0'
                                },
                                "links" : [],
                                "id" : item['id'],
                                "text" : item['message'],
                                "date": created_time, 
                            }
                            
                            url_regex = re.compile('(?:http|https|ftp):\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
                            
                            for url in url_regex.findall(item['message']):
                                post['links'].append({ 'href' : url })
                            post['user']['avatar'] = "http://graph.facebook.com/%s/picture" % item['from']['id']
                            
                            if 'to' in item:
                                post['to_users'] = item['to']['data']
                            
                            if 'likes' in item:
                                post['likes'] = item['likes']['count']
                            
                            subscribers_estimate = 0
                            
                            if item['from']['id'] in decoded_profiles:
                                activity = 0
                                
                                for profile_item in decoded_profiles[item['from']['id']]['data']:
                                    activity += profile_item['comments']['count']
                                    if 'likes' in profile_item:
                                        activity += profile_item['likes']['count']
                                
                                subscribers_estimate = activity * 10
                            
                            if subscribers_estimate < 130:
                                post['user']['subscribers'] = 130
                            else:
                                post['user']['subscribers'] = subscribers_estimate
                                # More research needs to be done into making a more accurate multiplier
                                # what is the rough percentage of total friends someone has vs. how many
                                # actuall participate on their wall on a regular basis?
                                # We can only do our best consistant guess, as Facebook does not tell us
                                # how many friends someone has. We can only guess by activity.
                            queue.put(post)

                
            sleep(2) # time between requests this is actually seconds * num_queries
