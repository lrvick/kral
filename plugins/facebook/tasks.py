import urllib2,json,time,datetime,stomp
from celery.task import PeriodicTask, Task
from celery.task import control
from celery.contrib.abortable import AbortableTask
from celery.task.control import inspect
from celery.execute import send_task 
from models import FacebookUser, FacebookPost
from kral.tasks import *
from kral.models import Query
from django.core.cache import cache
from django.conf import settings

class Facebook(Task):
    def run(self, querys, abort=False, **kwargs):
        i = inspect()
        for query in querys:
            FacebookFeed.delay(query)

class FacebookFeed(Task):
    def run(self,query,prev_url='none', **kwargs):
        logger = self.get_logger(**kwargs)
        if prev_url == 'none':
            url = "https://graph.facebook.com/search?q=%s&type=post&limit=25" % query
        else:
            url = prev_url
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return e
        try:
            paging = data['paging'] #next page / previous page urls
            prev_url = paging['previous']
            items = data['data']
        except:
            prev_url = prev_url
            time.sleep(5)
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_querys = Query.objects.order_by('last_processed')[:slots]
        if query in all_querys:
            FacebookFeed.delay(query,prev_url)
            try:
                items
                for item in items:
                    ProcessFBPost.delay(item,query)
                return "Spawned Processors"
            except:
                return "No data"
        else:
            return "Exiting Feed"
   
class ProcessFBPost(Task):
    def run(self, item, query, **kwargs):
        if item.has_key('message'):
            logger = self.get_logger(**kwargs)
            time_format = "%Y-%m-%dT%H:%M:%S+0000"
            data, from_user, to_users = {}, {}, {}
            if item.has_key('properties'): item.pop('properties') 
            if item.has_key('application'):
                application = item['application']
                if application:
                    data['application_name'] = application['name']
                    data['application_id'] = application['id']
                item.pop('application') 

            if item.has_key('likes'):
                data['likes'] = item['likes']['count']
                item.pop('likes')
            for k,v in item.items():
                if k == 'id':
                    data.update({'post_id': v })
                elif k == 'from':
                    from_user = item.pop('from') 
                elif k == 'to':
                    to_users = item.pop('to')
                elif k == 'created_time':
                    data.update({ k : datetime.datetime.strptime(v, time_format)})
                elif k == 'updated_time':
                    data.update({ k : datetime.datetime.strptime(v, time_format)})
                else:
                    data.update({ k : v })
            post_info = {
                    "service" : 'facebook',
                    "user" : from_user["name"],
                    "message" : data["message"],
            }
            conn = stomp.Connection()
            conn.start()
            conn.connect()
            conn.send(json.dumps(post_info), destination='/messages')
        return "Saved Post/User"
# vim: ai ts=4 sts=4 et sw=4
