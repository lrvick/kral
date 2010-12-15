import datetime
from django.http import HttpResponse
from django.core import serializers
from kral.plugins.twitter.models import *
from kral.models import *
from django.conf import settings
#currently hardcoding for twitter tweets only. will look at get_app / get_models for making it universal.

def serialize_model(request,model,query,format):
    query_object,created = Query.objects.get_or_create(text=query) 
    if hasattr(settings, 'KRAL_WAIT') and settings.KRAL_WAIT: 
        sec = datetime.timedelta(seconds=settings.KRAL_WAIT)
        if query_object.last_modified + sec <= datetime.datetime.now():
            query_object.last_modified = datetime.datetime.now()
            query_object.save() 
    else:
        query_object.last_modified = datetime.datetime.now()
        query_object.save() 
    query_object = Query.objects.get(text__iexact=query)
    results = serializers.serialize(format, query_object.twittertweet_set.all())
    return HttpResponse(results)



