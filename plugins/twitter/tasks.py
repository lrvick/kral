import urllib2,json,base64,datetime,pickle,rfc822,re
from django.conf import settings
from django.core.cache import cache
from celery.task.base import PeriodicTask, Task
from celery.result import AsyncResult
from kral.views import push_data, fetch_queries
    
class Twitter(PeriodicTask):
    run_every = getattr(settings, 'KRAL_WAIT', 5)
    def run(self, **kwargs):
        queries = fetch_queries()
        if getattr(settings, 'KRAL_TWITTER_FIREHOSE', False) is not True:
            for query in queries:
                if '_' in query:
                    queries.append(query.replace('_',''))
                    cache_name = "facebookstream_%s" % query
                    if cache.get(cache_name):
                        previous_result = AsyncResult(cache.get(cache_name))
                        if previous_result.ready():
                            result = TwitterFeed.delay(query)
                            cache.set(cache_name,result.task_id)
                    else:
                        result = TwitterFeed.delay(query)
                        cache.set(cache_name,result.task_id)
        if cache.get('twitterfeed'):
            previous_queries = pickle.loads(cache.get('twitterfeed_queries'))
            previous_result = AsyncResult(cache.get('twitterfeed'))
            if previous_result.ready():
                result = TwitterStream.delay(queries)
                cache.set('twitterfeed',result.task_id)
            if queries != previous_queries:
                result = TwitterStream.delay(queries)
                previous_result.revoke()
                cache.set('twitterfeed_queries',pickle.dumps(queries))
                cache.set('twitterfeed',result.task_id)
        else:
            result = TwitterStream.delay(queries)
            cache.set('twitterfeed_queries',pickle.dumps(queries))
            cache.set('twitterfeed',result.task_id)
            return

class TwitterFeed(Task):
    def run(self, query, **kwargs):
        cache_name = "twitter_lastid_%s" % query
        if cache.get(cache_name):
            url = "http://search.twitter.com/search.json?q=%s&since_id=%s" % (query.replace('_','+'),cache.get(cache_name))
        else:
            url = "http://search.twitter.com/search.json?q=%s&" % query.replace('_','+')
        try:
            data = json.loads(urllib2.urlopen(url).read())
            items = data['results']
            for item in items:
                TwitterFeedTweet.delay(item, query)
                cache.set(cache_name,str(item['id']))
            return
        except urllib2.HTTPError, error:
            logger.error("Twitter API returned HTTP Error: %s - %s" % (error.code,url))

class TwitterFeedTweet(Task):
    def run(self, item, query, **kwargs):
        logger = self.get_logger(**kwargs)
        if item.has_key('text'):
            post_info = {
                "service" : 'twitter',
                "user" : {
                    "name": item['from_user'],
                    "id": item['from_user_id_str'],
                    'avatar' : item['profile_image_url'],
                },
                "links" : [],
                "id" : item['id_str'],
                "text" : item['text'],
                "source": item['source'],
                "date": str(datetime.datetime.fromtimestamp(rfc822.mktime_tz(rfc822.parsedate_tz(item['created_at'])))),
            }
            url_regex = re.compile('(?:http|https|ftp):\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
            for url in url_regex.findall(item['text']):
                post_info['links'].append({ 'href' : url })
            push_data(post_info, queue=query)

class TwitterStream(Task):
    def run(self, queries, **kwargs):
        for query in queries:
            if getattr(settings, 'KRAL_TWITTER_FIREHOSE', False) is not True:
                if '_' in query:
                    queries.remove(query)
        logger = self.get_logger(**kwargs)
        self.query_post = str("track="+",".join([q for q in queries]))
        self.httprequest = urllib2.Request('http://stream.twitter.com/1/statuses/filter.json',self.query_post)
        self.auth = base64.b64encode('%s:%s' % (settings.TWITTER_USER, settings.TWITTER_PASS))
        self.httprequest.add_header('Authorization', "basic %s" % self.auth)
        try:
            self.stream = urllib2.urlopen(self.httprequest)
        except Exception,e:
            if e.code == 420:
                self.logger.info("Twitter connection closed")
            else:
                self.logger.error("Invalid/null response from server: %s" % (e))
        for tweet in self.stream:
            TwitterStreamTweet.delay(tweet, queries)

class TwitterStreamTweet(Task):
    def run(self, data, queries, **kwargs):
        logger = self.get_logger(**kwargs)
        content = json.loads(data)
        time_format = "%a %b %d %H:%M:%S +0000 %Y"
        if content["user"].get('id_str', None):
            post_info = { 
                'service' : 'twitter',
                'user' : {
                    'id' : content['user']['id_str'],
                    'utc' : content['user']['utc_offset'],
                    'name' : content['user']['screen_name'],
                    'description' : content['user']['description'],
                    'location' : content['user']['location'],
                    'avatar' : content['user']['profile_image_url'],
                    'subscribers': content['user']['followers_count'],
                    'subscriptions': content['user']['friends_count'],
                    'website': content['user']['url'],
                    'language' : content['user']['lang'],
                },
                'links' : [],
                'id' : content['id'],
                'application': content['source'],
                'date' : str(datetime.datetime.strptime(content['created_at'],time_format)),
                'text' : content['text'],
                'geo' : content['coordinates'],
            }
            for url in content['entities']['urls']:
                post_info['links'].append({ 'href' : url.get('url') })
            for query in [q.lower() for q in queries]:
                ns_query = query.replace('_','')
                if ns_query in content['text'].lower():
                    push_data(post_info, queue=ns_query)
            return

#vim: ai ts=5 sts=4 et sw=4
