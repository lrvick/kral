import json
import logging
import os
import sys
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
        sample_config_file = '%s/kral/docs/config.ini.sample' % os.path.dirname(sys.path[0])
        fh = open(sample_config_file,"r")
        sample_config = fh.read()
        fh.close()
        fh = open(config_file,"w")
        fh.write(sample_config)
        fh.close()

    fp = open(config_file)
    return fp


def fetch_json(request):
    """
    Returns json data from a given request/url but
    does more robust error handling. Will return 
    nothing if encounters an error.

    Arguments:
    request -- A urllib2 Request or url.

    """
    
    data = None 

    try:
        data = json.loads(urllib2.urlopen(request).read())
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print("Failed to reach a server.")
            print("Reason:", e.reason)
        elif hasattr(e, 'code'):
            print("The server couldn't fulfill the request.")
            print("Error code:", e.code)
    except Exception, e:
        print("Something else went wrong.")
        print(e)
    
    return data
    
