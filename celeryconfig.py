from kral import settings

#Celery Configs
BROKER_HOST = 'localhost'
BROKER_POST = 5672
BROKER_USER = 'guest'
BROKER_PASSOWRD = ''
BROKER_VHOST = ''

CELERY_RESULT_BACKEND = 'redis'
CELERY_IMPORTS = ('kral.tasks',) 

CELERY_RESULT_BACKEND = 'redis'
REDIS_HOST = getattr(settings, 'REDIS_HOST')
REDIS_PORT = getattr(settings, 'REDIS_PORT')
REDIS_DB   = getattr(settings,   'REDIS_DB')
REDIS_CONNECT_RETRY = True

