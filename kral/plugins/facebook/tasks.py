from celery.task import PeriodicTask, Task
from datetime import timedelta, datetime
from models import FacebookUser, FacebookPost
import urllib2
import json

class Facebook(PeriodicTask):
    
    run_every = timedelta(seconds=10)
     
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

        #store attribtues for model
        data = {}
        
        pdict = {}
        if item.has_key('properties'):
            pdict.update({'properties': item.pop('properties')[0]}) 
        
        #build fields/attrib dict to unpack to model - do some name mangling to fit model fields
        for k,v in item.items():
            if k == 'id':
                data.update({'post_id': v })
            elif k == 'from':
                data.update({'from_user': v })
            elif k == 'to':
                data.update({'to_users': v })
            elif k == 'picture':
                data.update({'picture_link': v })
            elif k == 'type':
                data.update({'post_type': v })
            elif k == 'created_time' or k == 'updated_time':
                data.update({ k : datetime.strptime(v, time_format)})
            else:
                data.update({ k : v })

        #relations need to be handled seperately
        from_dict, to_dict = {}, {}
        if data.has_key('from_user'):
            from_dict = data.pop('from_user')
        if data.has_key('to_users'):
            to_dict = data.pop('to_users')
        
        fbpost, created = FacebookPost.objects.get_or_create(**data)
        if created:
            logger.info("Saved new FacebookPost: %s" % fbpost)

        #store relations
        if from_dict:
            fbuser, created = FacebookUser.objects.get_or_create(
                user_id = from_dict['id'],
                name = from_dict['name'],
            )
            if created:
                logger.info("Saved new FacebookUser: %s" % fbuser)
            fbpost.from_user =  fbuser

        if to_dict:
            for userinfo in to_dict['data']:
                fbuser, created = FacebookUser.objects.get_or_create(
                    user_id = userinfo['id'], 
                    name = userinfo['name'],
                )
                fbpost.to_users.add(fbuser)

        if pdict:
            req_keys = ['name', 'href', 'text']
            
            for key in req_keys:
                if key not in pdict.keys():
                    pdict.update({key: ""})

            fbpost.properties_name = pdict['name'] 
            fbpost.properties_href = pdict['href']
            fbpost.properties_text = pdict['text']

        fbpost.save()


# vim: ai ts=4 sts=4 et sw=4
 
