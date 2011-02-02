import json,time,urllib2
from django.conf import settings
from django.core.cache import cache
from celery.task import PeriodicTask, Task
from celery.result import AsyncResult
from kral.views import push_data, fetch_queries

class Wordpress(PeriodicTask):
    run_every = getattr(settings, 'KRAL_WAIT', 5)
    def run(self, **kwargs):
        queries = fetch_queries()
        for query in queries:
            cache_name = "wordpressfeed_%s" % query
            if cache.get(cache_name): 
                previous_result = AsyncResult(cache.get(cache_name))
                if previous_result.ready():
                    result = WordpressFeed.delay(query)
                    cache.set(cache_name,result.task_id)
            else:
                result = WordpressFeed.delay(query)
                cache.set(cache_name,result.task_id)

class WordpressFeed(Task):
    def run(self, query, **kwargs):
        logger = self.get_logger(**kwargs)
        url = "http://en.search.wordpress.com/?q=%s&s=date&f=json" % query
        cache_name = "wordpressfeed_lastid_%s" % query
        last_seen = cache.get(cache_name,None)
        try:
            posts = json.loads(urllib2.urlopen(url).read())
        except urllib2.HTTPError, error:
            logger.error("HTTP Error: %s - %s" % (error.code,url))
            posts = None
        if posts:
            for post in posts:
                if last_seen:
                    if int(post['epoch_time']) > int(last_seen):
                        WordpressEntry.delay(post, query)
                        logger.info("Processing new post.")
                        cache.set(cache_name,post['epoch_time'])
                else:
                    WordpressEntry.delay(post, query)
                    cache.set(cache_name,post['epoch_time'])

class WordpressEntry(Task):
    def run(self, post, query, **kwargs):
        logger = self.get_logger(**kwargs)
        post_info = {
                "service" : 'wordpress',
                "date": post['epoch_time'],
                "user": {
                    "name":post['author'],
                },
                "text":post['content'],
                "source":post['guid'],

        }
        print(post_info)
        push_data(post_info, queue=query)
        logger.info("Pushed Wordpress Post data.")

