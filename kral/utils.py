# -*- coding: utf-8 -*-
import json
from eventlet.green import urllib2

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
