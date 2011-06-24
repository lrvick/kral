"""
Kral configuration

"""

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S+0000"

#KRAL_PLUGINS = ['facebook', 'twitter', 'buzz', 'wordpress', 'youtube', 'flickr'] #'identica',
KRAL_PLUGINS = ['facebook']
KRAL_SLOTS = 10
KRAL_TIME = 5
KRAL_USERAGENT = 'KralBot' 

BUZZ_API_KEY = ''
FLICKR_API_KEY = ''
FACEBOOK_API_KEY = ''
TWITTER_USER = ''
TWITTER_PASS = ''

#Temporary memcache settings
MEMCACHE_BACKEND = 'localhost:11211'

# Redis Settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
REDIS_DB = 1
