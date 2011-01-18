import urllib2, json, datetime, time
from celery.task import Task
from kral.tasks import *
from kral.models import Query
from kral.views import push_data
from django.conf import settings

last_id = None

class Identica(Task):
    def run(self, querys, **kwargs):
        for query in querys:
            IdenticaFeed.delay(query)

class IdenticaFeed(Task):
    def run(self, query, since_id=None, **kwargs):
        global last_id
        logger = self.get_logger(**kwargs)
        if last_id: 
            url = "http://identi.ca/api/search.json?q=%s&since_id=%s" % (query, since_id)
        else: #first time through
            url = "http://identi.ca/api/search.json?q=%s" % query
        try:
            data = json.loads(urllib2.urlopen(url).read())
            completed_in = data['completed_in']
            refresh_url = data['refresh_url']
            results = data['results']
            since_id = data['since_id']
            results_per_page = data['results_per_page']
            max_id = data['max_id']
            page = data['page'] 
            if not data['results']: 
                time.sleep(10)
                IdenticaFeed.delay(query, since_id=last_id)
            last_id = data['results'][0]['since_id'] #latest since_id will be used as last_id
        except Exception, e:
            raise e

        slots = gettattr(settings, 'KRAL_SLOTS', 1)
        all_querys = Query.objects.order_by('last_processed')[:slots]
        if query in all_querys:
            for item in data['results']:
                ProcessIdenticaPost.delay(item, query)
                logger.info("Sending IdenticaFeed item to be processed.")
        else:
            return

class ProcessIdenticaPost(Task):
    def run(self, item, query, **kwargs):
        logger = self.get_logger(**kwargs)
        time_format = "%a, %d %b %Y %H:%M:%S +0000"
        
        #NOTE: still some useful data to map, to_user, language code, etc.
        post_info = {
            "service": "identi.ca", 
            "user": {
                "name": item['from_user'],
                "id": item['from_user_id'],
            },
            "text": item['text'],
            "date": datetime.datetime.strptime(item['created_date'], time_format),
            "pictures": {
                "0": item['profile_image_url'],
            },
            "source": item['source'],
        }
        push_data(post_info, 'messages')
        logger.info("Saved Identica Post")
