import urllib2,json,time,datetime,stomp
from celery.task import Task
from kral.tasks import *
from kral.models import Query
from django.conf import settings

class Youtube(Task):
    def run(self, querys, abort=False, **kwargs):
        for query in querys:
            YoutubeFeed.delay(query)

class YoutubeFeed(Task):
    def run(self,query,**kwargs):
        logger = self.get_logger(**kwargs)
        url = "http://gdata.youtube.com/feeds/api/videos?q=%s&orderby=published&start-index=11&max-results=10&v=2&alt=json" % query
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return e
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_querys = Query.objects.order_by('last_processed')[:slots]
        if query in all_querys:
            try:
                for item in data['feed']['entry']:
                    ProcessYTVideo.delay(item,query)
                return "Spawned Processors"
            except:
                return "No data"
            time.sleep(5)
            YoutubeFeed.delay(query)
        else:
            return "Exiting Feed"
   
class ProcessYTVideo(Task):
    def run(self, item, query, **kwargs):
        if item.has_key('title'):
            logger = self.get_logger(**kwargs)
            post_info = {
                    "service" : 'youtube',
                    #"user" : from_user["name"],
                    "message" : item["title"]['$t'],
            }
            #print post_info['message']
            conn = stomp.Connection()
            conn.start()
            conn.connect()
            conn.send(json.dumps(post_info), destination='/messages')
        return "Saved Post/User"

# vim: ai ts=4 sts=4 et sw=4
