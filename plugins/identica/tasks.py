import urllib2, json, datetime, time
from celery.task import Task
from kral.tasks import *
from kral.models import Query
from kral.views import push_data
from django.conf import settings

last_id = None

class Identica(Task):
    def run(self, queries, **kwargs):
        for query in queries:
            IdenticaFeed.delay(query)

class IdenticaFeed(Task):
    def run(self, query, since_id=None, **kwargs):
        global last_id
        logger = self.get_logger(**kwargs)
        if since_id: 
            url = "http://identi.ca/api/search.json?q=%s&since_id=%s&rpp=100" % (query, since_id)
        else: #first time through
            url = "http://identi.ca/api/search.json?q=%s&rpp=100" % query
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
            last_id = data['results'][0]['id'] #latest since_id will be used as last_id
        except Exception, e:
            raise e

        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_queries = Query.objects.order_by('last_processed')[:slots]
        if query in all_queries:
            for item in data['results']:
                ProcessIdenticaPost.delay(item, query)
                logger.info("Sending IdenticaFeed item to be processed.")
        else:
            return

class ProcessIdenticaPost(Task):
    def run(self, item, query, **kwargs):
        logger = self.get_logger(**kwargs)
        time_format = "%a, %d %b %Y %H:%M:%S +0000"
        date = str(datetime.datetime.strptime(item['created_at'], time_format))
        
        post_info = {
            "service": "identi.ca", 
            "user": {
                "name": item['from_user'],
                "id": item['from_user_id'],
            },
            "to_user": {
                "name": item['to_user'],
                "id": item['to_user_id'],
            }, 
            "text": item['text'],
            "date": date,
            "pictures": {
                "0": {
                    "thumbnail": item['profile_image_url'],
                },
            },
            "source": item['source'],
            "id": item['id'], 
        }
        print(post_info['id'])
        push_data(post_info, queue = query)
        logger.info("Saved Identica Post")
