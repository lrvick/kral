from celery.task import PeriodicTask, Task
from datetime import timedelta, datetime
from models import FacebookUser, FacebookPost
from celery.execute import send_task 

import urllib2
import json

class Facebook(PeriodicTask):
    
    run_every = 10 #run every 10s
     
    def run(self, query="love", **kwargs): #temp hardcoded query
        logger = self.get_logger(**kwargs)
        logger.info("Executing every 10 seconds...")

        url = "https://graph.facebook.com/search?q=%s&type=post&limit=100" % query #get 100 at a time 
        
        try:
            data = json.loads(urllib2.urlopen(url).read())
        except Exception, e:
            return
        
        paging = data['paging'] #next page / previous page urls
        items = data['data']
        
        for item in items:
            ProcessFBPost.delay(item)
   
class ProcessFBPost(Task):
    
    def run(self, item, **kwargs):
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
        
        #build fields/attrib dict to unpack to model - do some name mangling to fit model fields
        for k,v in item.items():
            if k == 'id':
                data.update({'post_id': v })
            elif k == 'from':
                from_user = item.pop('from') 
            elif k == 'to':
                to_users = item.pop('to')
            elif k == 'created_time':
                data.update({ k : datetime.strptime(v, time_format)})
            elif k == 'updated_time':
                data.update({ k : datetime.strptime(v, time_format)})
            else:
                data.update({ k : v })

        fbpost, created = FacebookPost.objects.get_or_create(**data)
        if created:
            logger.info("Saved new FacebookPost: %s" % fbpost)

        #hand off url to be processed
        if fbpost.link:
            send_task("kral.tasks.ExpandURL", [fbpost.link])

        #store relations
        if from_user:
            fbuser, created = FacebookUser.objects.get_or_create(
                user_id = from_user['id'],
                name = from_user['name'],
            )
            if created:
                logger.info("Saved new FacebookUser: %s" % fbuser)
            fbpost.from_user =  fbuser

        if to_users:
            for user in to_users['data']:
                fbuser, created = FacebookUser.objects.get_or_create(
                    user_id = user['id'], 
                    name = user['name'],
                )
                fbpost.to_users.add(fbuser)

        #update all relations and save obj
        fbpost.save()


# vim: ai ts=4 sts=4 et sw=4
 
