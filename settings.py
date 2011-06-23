"""
Kral configuration

"""
import os

PLUGIN_DIR = "plugins"
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
PLUGIN_DIR_PATH = os.path.join(PROJECT_PATH, PLUGIN_DIR)

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
