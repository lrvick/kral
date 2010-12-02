import os
from django.conf import settings

for plugin in [x for x in os.listdir(os.path.join(settings.PROJECT_PATH,'kral/plugins')) if not x.startswith('__')]:
	#__import__('kral.plugins.'+plugin+'.models')
	exec('from kral.plugins.'+plugin+'.models import *')
