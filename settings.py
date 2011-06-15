"""
kral specific settings.
"""
import os

PLUGIN_DIR = "plugins"
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
PLUGIN_DIR_PATH = os.path.join(PROJECT_PATH, PLUGIN_DIR)

KRAL_PLUGINS = ['facebook', 'twitter', 'buzz', 'wordpress', 'youtube', 'flickr'] #'identica',
KRAL_SLOTS = 10
KRAL_TIME = 5
KRAL_USERAGENT = 'KralBot' 


REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_DB = 1

MEMCACHE_BACKEND = 'localhost:11211'

BUZZ_API_KEY = ''
FLICKR_API_KEY = ''
FACEBOOK_API_KEY = ''
TWITTER_USER = ''
TWITTER_PASS = ''
