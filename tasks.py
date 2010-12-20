import httplib,urlparse,time,re,sys,time,datetime,os
from celery.task.base import Task
from django.conf import settings
from kral.models import *

if not hasattr(settings, "KRAL_PLUGINS"): 
    for plugin in [x.lower() for x in os.listdir(os.path.join(settings.PROJECT_PATH,'kral/plugins')) if not x.startswith('__')]:
	    __import__('kral.plugins.'+plugin+'.tasks', fromlist=["*"])
else:
    for plugin in settings.KRAL_PLUGINS:
        plugin = plugin.lower()
        try:
	        __import__('kral.plugins.'+plugin+'.tasks', fromlist=["*"])
        except ImportError:
            raise ImportError('Module %s does not exist.' % plugin)

class ExpandURL(Task):
    def run(self,url,n=1,original_url=None,**kwargs):
        if n == 1:
            original_url = url
        logger = self.get_logger(**kwargs)
        headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"}
        parsed_url = urlparse.urlsplit(url)
        request = urlparse.urlunsplit(('', '', parsed_url.path, parsed_url.query, parsed_url.fragment))
        connection = httplib.HTTPConnection(parsed_url.netloc)
        try : 
            connection.request('HEAD', request, "", headers)
            response = connection.getresponse()
        except:
            return "Connection request failed"
        current_url = response.getheader('Location')
        n += 1
        if n > 3 or current_url == None:
            ProcessURL.delay(url)
            logger.info("Expanded URL \"%s\" to \"%s\"" % (original_url,url))
            return True
        else:
            ExpandURL.delay(current_url, n)

class ProcessURL(Task):
    def run(self,url,**kwargs):
        logger = self.get_logger(**kwargs)
        try:
            old_link = WebLink.objects.get(url=url)
            old_link.total_mentions += 1
            old_link.save()
            logger.info("Recorded mention of known URL: \"%s\"" % (url))
        except WebLink.DoesNotExist:
            weblink = WebLink.objects.create(url=url)
            logger.info("Added record for new URL: \"%s\"" % (url))
            return True

#vim: ai ts=4 sts=4 et sw=4