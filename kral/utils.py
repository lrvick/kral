import json
import logging
import os
from eventlet.green import urllib2


def config_init(config_file=None):
    """ Initialize config with default values if it does not exist """

    if not config_file:
        config_file = os.path.expanduser('~/.kral/config.ini')
    else:
        config_file = os.path.expanduser(config_file)

    if not os.path.exists(os.path.dirname(config_file)):
        os.makedirs(os.path.dirname(config_file))

    if not os.path.exists(config_file):
        sample_config_file = '%s/docs/config.ini.sample' % os.path.dirname(os.getcwd())
        fh = open(sample_config_file,"r")
        sample_config = fh.read()
        fh.close()
        fh = open(config_file,"w")
        fh.write(sample_config)
        fh.close()

    fp = open(config_file)
    return fp


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
