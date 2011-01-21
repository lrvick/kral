import urllib2,json,time,datetime
from celery.task import PeriodicTask, Task
from celery.task import control
from celery.contrib.abortable import AbortableTask
from celery.execute import send_task 
from models import FacebookUser, FacebookPost
from kral.tasks import *
from kral.models import Query
from kral.views import push_data
from django.core.cache import cache
from django.conf import settings

class Facebook(Task):
    def run(self, querys, abort=False, **kwargs):
        for query in querys:
            FacebookFeed.delay(query)

class FacebookFeed(Task):
    def run(self,query,prev_url=None, **kwargs):
        logger = self.get_logger(**kwargs)
        if not prev_url:
            url = "https://graph.facebook.com/search?q=%s&type=post&limit=25" % query
        else:
            url = prev_url
        try:
            data = json.loads(urllib2.urlopen(url).read())
            items = data['data']
        except Exception, e:
            raise e
        try:
            paging = data['paging'] #next page / previous page urls
            prev_url = paging['previous']
        except: #no previous url
            prev_url = prev_url
            time.sleep(5)
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_querys = Query.objects.order_by('last_processed')[:slots]
        if query in all_querys:
            FacebookFeed.delay(query, prev_url)
            for item in items:
                ProcessFBPost.delay(item, query)
                logger.info("Spawned Processors")
        else:
            logger.info("Exiting Feed")
   
class ProcessFBPost(Task):
    def run(self, item, query, **kwargs):
        logger = self.get_logger(**kwargs)
        time_format = "%Y-%m-%dT%H:%M:%S+0000"
        if item.has_key('message'):
            post_info = {
                    "service" : 'facebook',
                    "user" : {
                        "name": item['from']['name'],
                        "id": item['from']['id'],
                    },
                    "id" : item["id"],
                    "text" : item["message"],
                    "date": str(datetime.datetime.strptime(item['created_time'], time_format)),
            }
            if item.get('to'):
                post_info["to_users"] = item['to']['data']
            if item.get('likes'):
                post_info["likes"] = item['likes']['count']
            if item.get('application'):
                post_info["application"] = item['application']['name']
            push_data(post_info, queue=query)
            logger.info("Saved Post/User")

# vim: ai ts=4 sts=4 et sw=4
