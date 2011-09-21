import json
from eventlet.green import urllib2
import logging

def fetch_json(service,url):
    try:
        data = json.loads(urllib2.urlopen(url).read())
        return data
    except urllib2.HTTPError, error:
        logging.error("%s API returned HTTP Error: %s - %s" % (service,error.code,url))
        return None
    except urllib2.URLError, error:
        logging.error("%s API returned URL Error: %s - %s" % (service,error,url))
        return None
