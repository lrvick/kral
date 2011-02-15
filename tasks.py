import httplib,urlparse,re,sys,os,datetime,djcelery,pickle
from django.conf import settings
from django.core.cache import cache
from celery.task.control import inspect
from celery.decorators import task
from celery.signals import worker_ready,beat_init
from celery.execute import send_task
from kral.views import push_data

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

def kral_init(**kwargs):
    from djcelery.models import PeriodicTask,PeriodicTasks
    PeriodicTask.objects.all().delete()
    PeriodicTasks.objects.all().delete()
    cache.clear()
beat_init.connect(kral_init) 

@task
def expand_url(url,query,n=1,original_url=None,**kwargs):
    if n == 1:
        original_url = url
    logger = expand_url.get_logger(**kwargs)
    headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"}
    parsed_url = urlparse.urlsplit(url)
    request = urlparse.urlunsplit(('', '', parsed_url.path, parsed_url.query, parsed_url.fragment))
    try:
        connection = httplib.HTTPConnection(parsed_url.netloc)
    except httplib.InvalidURL:
        logger.error("Unable to expand Invalid URL: %s" % url)
        return False
    try : 
        connection.request('HEAD', request, "", headers)
        response = connection.getresponse()
    except Exception, e:
        response = None
    if response:
        current_url = response.getheader('Location')
        n += 1
        if n > 3 or current_url == None:
            cache_name = "alllinks_%s" % str(query.replace(' ',''));
            try:
                links = pickle.loads(cache.get(cache_name))
            except:
                links = []
            new_link = False
            for link in links:
                if link['href'].decode('utf8') == url.decode('utf8'):
                    link['count'] = link['count'] + 1
                    new_link = True
                    post_info = link
            if new_link == False:
                post_info = {'service':'links','href':url,'count':1,'title':''}
                links.append(post_info)
            links = sorted(links, key=lambda link: link['count'],reverse=True)
            cache.set(cache_name, pickle.dumps(links),31556926)
            push_data(post_info,queue=query)
        else:
            expand_url.delay(current_url,query, n)

#vim: ai ts=4 sts=4 et sw=4
