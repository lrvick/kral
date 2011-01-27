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
    def run(self,query,prev_list=None,**kwargs):
        logger = self.get_logger(**kwargs)
        url = "http://gdata.youtube.com/feeds/api/videos?q=%s&orderby=published&max-results=25&v=2&alt=json" % query
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            raise e
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        all_queries = Query.objects.order_by('last_processed')[:slots]
        
        entries = data['feed']['entry']
        id_list = [e['id']['$t'].split(':')[-1] for e in entries]
        print("IDS: %s" % id_list)

        if query in all_queries:
            if prev_list:
                time.sleep(10)
            try:
                for entry in entries: 
                    if prev_list:
                        v_id = entry['id']['$t'].split(':')[-1]
                        #if current video id in previous ids we skip
                        if v_id in prev_list:
                            pass
                        else:
                            #this is new, so process it
                            print("%s is new, processing ..." % v_id)
                            ProcessYTVideo.delay(entry, query)
                    else:
                        #first time through, no previous list process videos
                        ProcessYTVideo.delay(entry, query)
                logger.info("Spawned Processors")
            except Exception, e:
                raise e
            YoutubeFeed.delay(query, id_list)
        else:
            logger.info("Exiting Feed")
   
class ProcessYTVideo(Task):
    def run(self, item, query, **kwargs):
        logger = self.get_logger(**kwargs)
        if item.has_key('title'):
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
