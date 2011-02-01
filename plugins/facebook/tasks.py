import urllib2,json,time,datetime,re,pickle
from django.conf import settings
from django.core.cache import cache
from celery.task import PeriodicTask, Task
from celery.task import control
from celery.result import AsyncResult
from celery.contrib.abortable import AbortableTask
from celery.execute import send_task 
from kral.tasks import *
from kral.models import Query
from kral.views import push_data

class Facebook(PeriodicTask):
    run_every = getattr(settings, 'KRAL_WAIT', 5)
    def run(self, **kwargs):
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        queries = Query.objects.order_by('last_processed')[:slots]
        if cache.get('facebook_tasks'):
            facebook_tasks = pickle.loads(cache.get('facebook_tasks'))
        else:
            facebook_tasks = {}
        for query in queries:
            try:
                previous_result = AsyncResult(facebook_tasks[str(query)])
                if previous_result.ready():
                    result = FacebookFeed.delay(query)
            except Exception, e:
                result = FacebookFeed.delay(query)
        if result:
            facebook_tasks[str(query)] = str(result.task_id)
            cache.set('facebook_tasks',pickle.dumps(facebook_tasks))
        
class FacebookFeed(Task):
    def run(self, query, **kwargs):
        logger = self.get_logger(**kwargs)
        cache_name = "facebook_prevurl_%s" % query
        if cache.get(cache_name):
            url = cache.get(cache_name)
        else:
            url = "https://graph.facebook.com/search?q=%s&type=post&limit=25" % query
        try:
            data = json.loads(urllib2.urlopen(url).read())
            items = data['data']
        except Exception, e:
            raise e
        try:
            prev_url = data['paging']['previous']
        except:
            prev_url = url
        for item in items:
            ProcessFBPost.delay(item, query)
        logger.info("Spawned Processors")
        cache.set(cache_name,str(prev_url))
        return True
   
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
                    'links' : [],
                    "id" : item['id'],
                    "text" : item['message'],
                    "date": str(datetime.datetime.strptime(item['created_time'], time_format)),
            }
            url_regex = re.compile('(?:http|https|ftp):\/\/[\w\-_]+(?:\.[\w\-_]+)+(?:[\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?')
            for url in url_regex.findall(item['message']):
                post_info['links'].append({ 'href' : url })
            post_info['user']['avatar'] = "http://graph.facebook.com/%s/picture" % item['from']['id']
            if item.get('to'):
                post_info['to_users'] = item['to']['data']
            if item.get('likes'):
                post_info['likes'] = item['likes']['count']
            if item.get('application'):
                post_info['application'] = item['application']['name']
            push_data(post_info, queue=query)
            logger.info("Saved Post/User")

# vim: ai ts=4 sts=4 et sw=4
