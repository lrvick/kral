import urllib2,json,time,datetime
from celery.task import Task
from kral.tasks import *
from kral.views import push_data
from kral.models import Query
from django.conf import settings

class Youtube(Task):
    def run(self, queries, abort=False, **kwargs):
        for query in queries:
            YoutubeFeed.delay(query)

class YoutubeFeed(Task):
    def run(self,query,prev_date='0',**kwargs):
        logger = self.get_logger(**kwargs)
        time_format = '%Y-%m-%dT%H:%M:%S.000Z'
        url = "http://gdata.youtube.com/feeds/api/videos?q=%s&orderby=published&max-results=25&v=2&alt=json" % query
        try:
            data = json.loads(urllib2.urlopen(url).read())
            first_post_date = data['feed']['entry'][0]['published']['$t']
            first_date = time.mktime(time.strptime(first_post_date,time_format))
            if int(first_date) < int(prev_date):
                first_date = prev_date
        except Exception, e:
            raise e
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_queries = Query.objects.order_by('last_processed')[:slots]
        if query in all_queries:
            if prev_date is not '0':
                time.sleep(10)
            YoutubeFeed.delay(query,first_date)
            try:
                for item in data['feed']['entry']:
                    this_date = time.mktime(time.strptime(item['published']['$t'],time_format))
                    if int(this_date) > int(prev_date):
                        ProcessYTVideo.delay(item,query)
                return "Spawned Processors"
            except:
                return "No data"
        else:
            return "Exiting Feed"
   
class ProcessYTVideo(Task):
    def run(self, item, query, **kwargs):
        if item.has_key('title'):
            logger = self.get_logger(**kwargs)
            print(item['media$group']['media$thumbnail'])
            post_info = {
                    "service" : 'youtube',
                    "id" : item['media$group']['yt$videoid']['$t'],
                    "date" : item['media$group']['yt$uploaded']['$t'],
                    "user" : item['author'][0]["name"]['$t'],
                    "source" : item['link'][1]['href'],
                    "text" : item["title"]['$t'],
                    "keywords" : item['media$group']['media$keywords'].get('$t',''),
                    "description" : item['media$group']['media$description']['$t'],
                    "thumbnail" : "http://i.ytimg.com/vi/%s/hqdefault.jpg" % item['media$group']['yt$videoid']['$t'],
                    "duration" : item['media$group']['yt$duration']['seconds'],
            }
            push_data(post_info, queue = query)
        logger.info("Saved Post/User")

# vim: ai ts=4 sts=4 et sw=4
