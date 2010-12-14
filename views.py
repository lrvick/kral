from django.utils import simplejson
from django.http import HttpResponse
from kral.plugins.twitter.models import *

#currently hardcoding for twitter tweets only. will look at get_app / get_models for making it universal.

def serialize_model(request,model,query,format):
    if format == 'json':
        data = TwitterTweet.objects.filter(text__search=query)
        return HttpResponse(str(data))

#        return HttpResponse(simplejson.dumps(data), mimetype="application/json")



