"""
Celery configuration

Documentation: http://ask.github.com/celery/configuration.html

"""

import settings

CELERY_IMPORTS = ('services.facebook','services.twitter')

CELERYD_POOL = 'eventlet'

CELERYD_CONCURRENCY = 300

CELERY_ALWAYS_EAGER = False

# Task Broker Backend Settings
BROKER_BACKEND = 'redis'
BROKER_HOST = getattr(settings, 'REDIS_HOST')
BROKER_PORT = getattr(settings, 'REDIS_PORT')
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = getattr(settings, 'REDIS_PASSWORD')

#Task Result Backend Settings
CELERY_RESULT_BACKEND = 'redis'
REDIS_HOST = getattr(settings, 'REDIS_HOST')
REDIS_PORT = getattr(settings, 'REDIS_PORT')
REDIS_PASSWORD = getattr(settings, 'REDIS_PASSWORD')
REDIS_DB   = getattr(settings, 'REDIS_DB')
REDIS_CONNECT_RETRY = True
