import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Starts all enabled kralrs'
    def handle(self, *args, **options):
        print "Starting Kralrs"
        if not hasattr(settings, "KRALRS_ENABLED"):
            for plugin in [x.lower() for x in os.listdir(os.path.join(settings.PROJECT_PATH,'kral/plugins')) if not x.startswith('__')]:
                exec('from kral.plugins.'+plugin+'.tasks import *')
                #This should dynamically start all enabled kralrs, but for now we hardcode
        Twitter.delay()
        Facebook.delay()

