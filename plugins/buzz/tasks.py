import urllib2,json,time,datetime
from celery.task import Task
from kral.tasks import *
from kral.models import Query
from kral.views import push_data
from django.conf import settings

class Buzz(Task):
    def run(self, querys, abort=False, **kwargs):
        for query in querys:
            BuzzFeed.delay(query)

class BuzzFeed(Task):
    def run(self,query,prev_date='0',**kwargs):
        logger = self.get_logger(**kwargs)
        time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        url = "http://www.googleapis.com/buzz/v1/activities/search?alt=json&orderby=published&q=%s" % query
        try:
            data = json.loads(urllib2.urlopen(url).read())
            dates = []
            for item in data['data']['items']:
                dates.append(int(time.mktime(time.strptime(item['updated'],time_format))))
            dates.sort()
            dates.reverse()
            first_date = dates[0]
            if int(first_date) < int(prev_date):
                first_date = prev_date
        except Exception, e:
            raise e
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_querys = Query.objects.order_by('last_processed')[:slots]
        if query in all_querys:
            if prev_date is not '0':
                time.sleep(10)
            BuzzFeed.delay(query,first_date)
            try:
                for item in data['data']['items']:
                    this_date = int(time.mktime(time.strptime(item['updated'],time_format)))
                    if int(this_date) > int(prev_date):
                        ProcessBuzzPost.delay(item,query)
                logger.info("Spawned Processors")
            except:
                return "No data"
        else:
            return "Exiting Feed"
   
class ProcessBuzzPost(Task):
    def run(self, item, query, **kwargs):
        logger = self.get_logger(**kwargs)
        time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        # FIXME should consider all pictures, not just one
        try: 
            thumbnail = item['object']['attachments'][0]['links']['preview'][0]['href']
            picture = item['object']['attachments'][0]['links']['enclosure'][0]['href']
        except:
            picture = ""
            thumbnail = ""
        # END FIXME
        post_info = {
                "service" : 'buzz',
                "user" : {
                    "name" : item['actor']['name'],
                    "id" : item['actor']['name'],
                    "avatar": item['actor']['thumbnailUrl'],
                    "source": item['actor']['profileUrl'], 
                },
                "pictures" : { # hard-coding for only one picture. See above FIXME
                    "0": {
                        "picture": picture,
                        "thumbnail": thumbnail,
                    },
                },
                "id" : item['id'].split(":")[3],
                "date" : str(datetime.datetime.strptime(item['published'],time_format)),
                "source" : item['object']['links']['alternate'][0]['href'],
                "text" : item["object"]['content'],
        }
        push_data(post_info, queue = query)
        logger.info("Saved Post/User")

# vim: ai ts=4 sts=4 et sw=4
