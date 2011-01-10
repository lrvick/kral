import httplib,urlparse,re,sys,os,datetime
from django.conf import settings
from celery.task.control import inspect
from celery.task.base import PeriodicTask,Task
from celery.signals import worker_ready
from celery.execute import send_task
from kral.models import *
from django.core.cache import cache

ALLPLUGINS = []

if not hasattr(settings, "KRAL_PLUGINS"): 
    for plugin in [x.lower() for x in os.listdir(os.path.join(settings.PROJECT_PATH,'kral/plugins')) if not x.startswith('__')]:
        __import__('kral.plugins.'+plugin+'.tasks', fromlist=["*"])
        ALLPLUGINS.append(plugin.title())
else:
    for plugin in settings.KRAL_PLUGINS:
        plugin = plugin.lower()
        try:
            __import__('kral.plugins.'+plugin+'.tasks', fromlist=["*"])
        except ImportError:
            raise ImportError('Module %s does not exist.' % plugin)

class PluginController(PeriodicTask):
    run_every = settings.KRAL_WAIT
    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        slots = getattr(settings, 'KRAL_SLOTS', 1)
        plugins = getattr(settings, 'KRAL_PLUGINS', ALLPLUGINS)
        querys = Query.objects.order_by('last_processed')[:slots]
        for query in querys:
            if cache.get(query.text):
                new_querys = False
            else:
                new_querys = True
        if new_querys:
            for plugin in plugins:
                send_task("kral.plugins.%s.tasks.%s" % (plugin.lower(), plugin.capitalize()), kwargs={'querys': querys })
                logger.debug("Started %s task for querys: %s" % (plugin, querys))
            cache.clear()
            for query in querys:
                cache.set(query.text,'1')
                query.save()
            print "REREUNNING STUFFS!"
            return "Refreshed tasks"
        else:
            print "NO MORE STUFFS TO RUN"
            return "No refresh needed"

class ExpandURL(Task):
    def run(self,url,query,n=1,original_url=None,**kwargs):
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
            ProcessURL.delay(url,query)
            logger.debug("Expanded URL \"%s\" to \"%s\"" % (original_url,url))
            return "Expanded URL"
        else:
            ExpandURL.delay(current_url,query, n)

class ProcessURL(Task):
    def run(self,url,query,**kwargs):
        logger = self.get_logger(**kwargs)
    
        weblink, created = WebLink.objects.get_or_create(url=url)
        if created:
            logger.debug("Added record for new URL: \"%s\"" % (url))
        else:
            weblink.total_mentions += 1
            weblink.save()
            logger.debug("Recorded mention of known URL: \"%s\"" % (url))
        
        qobj = Query.objects.get(text__iexact=unicode(query))
        weblink.querys.add(qobj)
        logger.debug("Added relation for weblink to: %s" % qobj)
        logger.debug("Added/Updated URL: %s" % url)



#vim: ai ts=4 sts=4 et sw=4
