import os
import datetime
import djcelery
import pickle
import urllib2
import base64
import urllib
import redis
import ewrl
from django.conf import settings
from celery.task.control import inspect
from celery.decorators import task
from celery.signals import worker_ready,beat_init
from celery.execute import send_task
from kral.views import push_data
from eventlet.timeout import Timeout

cache = redis.Redis(host='localhost', port=6379, db=1)

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
    task_cache = redis.Redis(host='localhost', port=6379, db=0)
    task_cache.flushdb()
    cache.set('KRAL_QUERIES',settings.KRAL_QUERIES)
beat_init.connect(kral_init) 

@task
def url_process(url,query,n=1,original_url=None,**kwargs):
    logger = url_process.get_logger(**kwargs)
    all_links_cache_name = "alllinks_%s" % str(query.replace(' ',''));
    expanded_cache_name = "expanded_%s" % base64.b64encode(url)
    url_expanded = cache.get(expanded_cache_name)
    if not url_expanded:
        with Timeout(10, False) as timeout:
            try:
                url_expanded = ewrl.url_expand(url)
                if url_expanded is False:
                    url_expanded = url
            except Timeout:
                logger.error("Timed out expanding URL: %s" % url)
                url_expanded = url
            except Exception, e:
                logger.error(e)
                url_expanded = url
            cache.set(expanded_cache_name,url_expanded)
    title_cache_name = "title_%s" % base64.b64encode(url_expanded)
    url_title = cache.get(title_cache_name)
    if not url_title:
        with Timeout(10, False) as timeout:
            try:
                url_title, url_feed = ewrl.url_data(url_expanded)
            except Timeout:
                logger.error("Timed out fetching title for URL: %s" % url_expanded)
                url_title = 'No Title'
            except Exception, e:
                logger.error(e)
                url_title = 'No Title'
            cache.set(title_cache_name,url_title)
    mentions_cache_name = "mentions_%s" % base64.b64encode(url_expanded)
    url_mentions_cached = cache.get(mentions_cache_name)
    if not url_mentions_cached:
        url_mentions = 1
    else:
        url_mentions = int(url_mentions_cached) + 1
    cache.set(mentions_cache_name,url_mentions)
    post_info = {'service':'links','href':url_expanded,'count':url_mentions,'title':url_title}
    try:
       links = pickle.loads(cache.get(all_links_cache_name))
    except:
        links = []
    new_link = True
    for link in links:
        if link['href'] == url_expanded:
            link['count'] += 1
            new_link = False
    if new_link:
        links.append(post_info)
    links = sorted(links, key=lambda link: link['count'],reverse=True)
    cache.set(all_links_cache_name, pickle.dumps(links))
    push_data(post_info,queue=query)

#vim: ai ts=4 sts=4 et sw=4
