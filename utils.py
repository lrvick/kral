import json
import urllib2

def fetch_json(service,logger,url):
    try:
        data = json.loads(urllib2.urlopen(url).read())
        return data
    except urllib2.HTTPError, error:
        logger.error("%s API returned HTTP Error: %s - %s" % (service,error.code,url))
        return None
    except urllib2.URLError, error:
        logger.error("%s API returned URL Error: %s - %s" % (service,error,url))
        return None
