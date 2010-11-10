#!/usr/bin/python
import httplib,urlparse,pycurl,json,time,re,sys,time,datetime,os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings

for plugin in [x for x in os.listdir(os.path.join(settings.PROJECT_PATH,'kral/plugins')) if not x.startswith('__')]:
	exec('from kral.plugins.'+plugin+'.kralr import *')

#it is not grabbing the class names. Twitter is not valid..,. hmm, one sec. I have to see if something is possible first

QUERY="beiber"

#this needs to be dynamic:
twitter_kralr = Twitter()

#vim: ai ts=4 sts=4 et sw=4
