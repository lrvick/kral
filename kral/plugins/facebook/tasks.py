from celery.task import PeriodicTask
from datetime import timedelta, datetime
from models import FacebookUser, FacebookStatus
import urllib2
import json

#TODO: possibly use recursion to keep calling run on the paging URLs until we hit
#i     an exception

class ProcessFBStatus(PeriodicTask):
    
    run_every = timedelta(seconds=30)

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
            if item['type'] == type:
                d = {}
                
                #'to' and 'attirbution' are special cases
                if item.has_key('to'): d.update({'to': item['to']}) #dict of users              
                #TODO: save new users if 'to' exists

                if item.has_key('attribution'): d.update({'attribution': item['attribution']})
                
                d.update({ #default attributes
                    'from_user_id' :  item['from']['id'],
                    'from_user_name' : items['from']['name'],
                    'updated_time' : datetime.strptime(item['updated_time'], time_format),
                    'created_time' : datetime.strptime(item['created_time'], time_format),
                    'message' : item['message'],
                    'type' : item['type'],
                    'status_id' : item['id'],
                })
        
                #save user if new
                try:
                    user = FacebookUser.objects.get(user_id=d['from_user_id'], name=d['from_user_name'])
                except FacebookUser.ObjectDoesNotExist:
                    user = FacebookUser()
                    user.user_id = d['from_user_id']
                    user.name = d['from_user_name']
                    user.save()

                #save status to db if new
               

# vim: ai ts=4 sts=4 et sw=4
 
