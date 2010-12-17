import os
from os.path import join as pjoin
from django.conf import settings

PPATH = pjoin(settings.PROJECT_PATH, "kral/plugins")
for d in os.listdir(PPATH):
    if os.path.isdir(PPATH + os.sep + d):
        __import__('kral.plugins.' + d + '.models', fromlist = ['*'])

