import json
import time
import urllib2
from celery.task import Task
from kral.models import Query
from kral.tasks import *
from kral.views import push_data
from django.conf import settings

class Wordpress(Task):
    def run(self, queries, abort=False, **kwargs):
        for query in queries:
            WordpressFeed.delay(query)

class WordpressFeed(Task):
    def run(self, query, last_seen=None, **kwargs):
        logger = self.get_logger(**kwargs)
        url = "http://en.search.wordpress.com/?q=%s&s=date&f=json" % query
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            raise e

        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_queries = Query.objects.order_by('last_processed')[:slots]
        
        posts = data

        if query in all_queries:
            for post in posts:
                if last_seen:
                    #process only posts that are newer than 'last_seen'
                    if int(post['epoch_time']) > int(last_seen):
                        ProcessWordpressPost(post, query)
                        logger.info("Processing new post.")
                else:
                    #if not last seen, first time, process.
                    ProcessWordpressPost(post, query)
        
            WordpressFeed.delay(query, last_seen=posts[0]['epoch_time'])
        else:
            logger.info("Query wasn't found in all queries, exiting task.")
            

class ProcessWordpressPost(Task):
    def run(self, post, query, **kwargs):
        logger = self.get_logger(**kwargs)
        post_info = {


        }
        push_data(post_info, queue=query)
        logger.info("Pushed Wordpress Post data.")

