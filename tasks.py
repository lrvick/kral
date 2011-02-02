import httplib,urlparse,re,sys,os,datetime,djcelery,pickle
from django.conf import settings
from django.core.cache import cache
from celery.task.control import inspect
from celery.task.base import PeriodicTask,Task
from celery.signals import worker_ready,beat_init
from celery.execute import send_task

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

    

#vim: ai ts=4 sts=4 et sw=4
