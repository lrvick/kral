import urllib2,json,base64,datetime,pickle
from django.conf import settings
from django.core.cache import cache
from celery.task.base import PeriodicTask, Task
from celery.result import AsyncResult
from kral.views import push_data, fetch_queries

class Twitter(PeriodicTask):
    run_every = getattr(settings, 'KRAL_WAIT', 5)
    def run(self, **kwargs):
        queries = fetch_queries()
        if cache.get('twitterfeed'):
            previous_queries = pickle.loads(cache.get('twitterfeed_queries'))
            previous_result = AsyncResult(cache.get('twitterfeed'))
            if previous_result.ready():
                result = TwitterFeed.delay(queries)
                cache.set('twitterfeed',result.task_id)
            if queries != previous_queries:
                result = TwitterFeed.delay(queries)
                previous_result.revoke()
                cache.set('twitterfeed_queries',pickle.dumps(queries))
                cache.set('twitterfeed',result.task_id)
        else:
            result = TwitterFeed.delay(queries)
            cache.set('twitterfeed_queries',pickle.dumps(queries))
            cache.set('twitterfeed',result.task_id)
            return

class TwitterFeed(Task):
    def run(self, queries, **kwargs):
        logger = self.get_logger(**kwargs)
        self.query_post = str("track="+",".join([q for q in queries]))
        self.request = urllib2.Request('http://stream.twitter.com/1/statuses/filter.json',self.query_post)
        self.auth = base64.b64encode('%s:%s' % (settings.TWITTER_USER, settings.TWITTER_PASS))
        self.request.add_header('Authorization', "basic %s" % self.auth)
        try:
            self.stream = urllib2.urlopen(self.request)
        except Exception,e:
            if e.code == 420:
                logger.info("Twitter connection closed")
            else:
                logger.error("Invalid/null response from server: %s" % (e))
        for tweet in self.stream:
            TwitterTweet.delay(tweet, queries)

class TwitterTweet(Task):
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
                if query in content['text'].lower():
                    push_data(post_info, queue=query)
            return

#vim: ai ts=5 sts=4 et sw=4
