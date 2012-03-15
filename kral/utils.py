import json
import os
from eventlet.green import urllib2
import imp
import shutil

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
DOC_PATH = '/'.join(PROJECT_PATH.split('/')[:-1]) + '/docs' 

def config_init(config_file=None):
    """Initializes and returns the config. 
    
    By default looks for config.py in the users ~/.kral dir.
    If no config file is found it will copy the sample one in its place.
    
    Arguments:
    config_file (str) -- Path to an optional config file.
    """

    config_path = os.path.expanduser('~/.kral')
    config_fname = 'config.py'
    
    if config_file:
        return imp.load_source(config_fname, config_file)
    else:
        config_file = os.path.join(config_path, config_fname)

    if not os.path.exists(os.path.join(config_path)):
        os.makedirs(config_path)

    if not os.path.exists(config_file):
        sample_config_path = os.path.join(DOC_PATH, 'config.py.sample')
        target_config_path = os.path.join(config_path, 'config.py')
        shutil.copy(sample_config_path, target_config_path)

    config = imp.load_source(config_fname, config_file)
    return config

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
    
