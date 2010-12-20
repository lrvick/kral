import datetime
from django.http import HttpResponse
from django.core import serializers
from kral.plugins.twitter.models import *
from kral.models import *
from django.conf import settings
#currently hardcoding for twitter tweets only. will look at get_app / get_models for making it universal.

def serialize_model(request,model,query,format):
    query_object,created = Query.objects.get_or_create(text=query) 
    query_object.last_modified = datetime.datetime.now()
    query_object.save() 
    query_object = Query.objects.get(text__iexact=query)
    results = serializers.serialize(format, query_object.twittertweet_set.all()[:1])
    return HttpResponse(results)



