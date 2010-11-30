#!/usr/bin/python
import httplib,urlparse,pycurl,json,time,re,sys,time,datetime,os,curses,threading
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import models
from django.conf import settings
from django.utils import importlib
from django.db.models import get_model

for plugin in [x for x in os.listdir(os.path.join(settings.PROJECT_PATH,'kral/plugins')) if not x.startswith('__')]:
    exec('from kral.plugins.'+plugin+'.tasks import *')

QUERY="love"

class Interface(threading.Thread):
    def __init__(self):
        self.screen = curses.initscr()
        self.screen.border(1)
        threading.Thread.__init__(self)
    def run(self):
        self.height, self.width = self.screen.getmaxyx()
        def getWidthFromPercent(percent):
            real_width=(float(self.width / 100) )* float(percent)
            return int(real_width)
        def getHeightFromPercent(percent):
            real_height=(float(self.height / 100) )* float(percent)
            return int(real_height)
        self.screen.addstr(0,getWidthFromPercent(50),'[ Kral Engine - Running ]')
        self.win1 = curses.newwin(getHeightFromPercent(25),getWidthFromPercent(100),2,2)
        self.win1.border(1)
        self.screen.refresh()
        while True:
            count = 0
            stats_string=""
            for model in models.get_models():
                if 'plugin' in model.__module__:
                    this_model = get_model('kral',model.__name__)
                    #string = len(this_model.objects.all()),model.__name__+"s"
                    vars()['plugin'+str(count)] = "%s %s" % (len(this_model.objects.all()),model.__name__+"s")
                    stats_string = vars()['plugin'+str(count)]+" | "+stats_string
                    count += 1
            #self.win1.addstr(2,2, str(this_model.objects.latest('last_modified').text.encode("utf-8")))
            self.win1.refresh()    
            self.screen.addstr(12,25, stats_string)
            self.screen.refresh()
            self.height, self.width = self.screen.getmaxyx()
            time.sleep(1)
            #print stats_string
            #print "real width is: %s" % (columns)
            #print "half width is: %s" % (getWidthFromPercent(50))
            #print "real height is: %s" % (rows)
            #print "half height is: %s" % (getHeightFromPercent(50))

#Interface().start()
#this needs to be dynamic:

#Twitter.delay(QUERY)
#twitter_kralr = Twitter(QUERY)
#facebook_kralr = Facebook(QUERY)

#vim: ai ts=4 sts=4 et sw=4
