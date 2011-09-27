import json
import logging
import os
from eventlet.green import urllib2
from ConfigParser import ConfigParser

def get_settings(config_file=None):
    """Returns array containing kral configuration settings

    If user configuration file does not exist, one is created with defaults
    """

    settings = {
        'TIME_FORMAT' : "%Y-%m-%dT%H:%M:%S+0000",
        'twitter': {
            'user':'',
            'pass':'',
        },
        'facebook': {
            'app_id':'',
            'app_secret':'',
            'access_token':'',
        },
        'identica': {
            'user':'',
            'pass':'',
        },
        'buzz': {
            'api_key':'',
        },
        'flickr': {
            'api_key':'',
        },
    }

    if config_file and os.path.exists(config_file):
        user_config_file = os.path.expanduser(config_file)
    else:
        user_config_file = os.path.expanduser('~/.kral/config.ini')

    sample_config_file = '%s/docs/config.ini.sample' % os.path.dirname(os.getcwd())

    if not os.path.exists(os.path.dirname(user_config_file)):
        os.makedirs(os.path.dirname(user_config_file))

    if not os.path.exists(user_config_file):
        fh = open(sample_config_file,"r")
        sample_config = fh.read()
        fh.close()
        fh = open(user_config_file,"w")
        fh.write(sample_config)
    else:
        config = ConfigParser()
        config.readfp(open(user_config_file))
        for section in config.sections():
            for key,value in config.items(section):
                settings[section.lower()][key.lower()] = value
        for key,value in config.items('DEFAULT'):
            settings[key.lower()] = value

    return settings

def fetch_json(service,url):
    """Returns json data from a given url

    Keyword aguments:
    service -- the name of the service
    url     -- the url to pull json data from

    """
    try:
        data = json.loads(urllib2.urlopen(url).read())
        return data
    except urllib2.HTTPError, error:
        logging.error("%s API returned HTTP Error: %s - %s" % (service,error.code,url))
        return None
    except urllib2.URLError, error:
        logging.error("%s API returned URL Error: %s - %s" % (service,error,url))
        return None
