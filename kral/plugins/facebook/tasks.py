from celery.task import PeriodicTask
from datetime import timedelta, datetime
from models import FacebookUser, FacebookStatus
import urllib2
import json

class Facebook(PeriodicTask):
    run_every = timedelta(seconds=30)
    self.query = query
    self.url = "https://graph.facebook.com/search?q=%s&type=post" % self.query 
    self.task = ProcessFBStatus.apply_async(args=[self.url, self.type])
    def run(self, url, type, **kwargs):
        logger = self.get_logger(**kwargs)
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return
        paging = data['paging'] #next page / previous page urls
        items = data['data']
        time_format = "%Y-%m-%dT%H:%M:%S+0000"
        for item in items:
            ProcessFBStatus.delay(item)
   
class ProcessFBStatus(Task):
    self.type = 'status'
    def run(self, item, **kwargs):
        if item['type'] == type:
            d = {}
            #'to' and 'attribution' are special cases
                
            #TODO: save new users if 'to' exists
            #if item.has_key('to'): d.update({'to': item['to']}) #dict of users              

            if item.has_key('attribution'): d.update({'attribution': item['attribution']})
                
            d.update({ #default attributes
                'updated_time' : datetime.strptime(item['updated_time'], time_format),
                'created_time' : datetime.strptime(item['created_time'], time_format),
                'message' : item['message'],
                'type' : item['type'],
                'status_id' : item['id'],
            })
            #save user if new
            user, created = FacebookUser.objects.get_or_create(user_id=item['from']['id'], name=item['from']['name'])
            if created:
                logger.info("Saved new FacebookUser: %s %s" % (user.user_id, user.name))

            d.update({'from_user': user})
            #save status to db if new
            fbstatus, created = FacebookStatus.objects.get_or_create(**d) 
            if created:
                logger.info("Saved new FacebookStatus: %s %s" % (fbstatus.status_id, fbstatus.message))

# vim: ai ts=4 sts=4 et sw=4
 
