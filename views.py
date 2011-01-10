import datetime
from django.http import HttpResponse, Http404
from django.core import serializers
from kral.plugins.twitter.models import *
from kral.plugins.facebook.models import *
from kral.models import *
from django.conf import settings

def serialize_model(request,plugin,query,format):
    query = query.lower()
    ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    visitor_object,created = Visitor.objects.get_or_create(ip=ip)
     
    query_object,created = Query.objects.get_or_create(text=query)
    query_object.last_modified = datetime.datetime.now()
    query_object.save()

    visitor_object.querys.add(query_object)

    try:
        qs = getattr(query_object, "%s_set" % plugin.lower())
    except AttributeError:
        raise Http404("Does not exist.")

    results = serializers.serialize(format, qs.all()[:10])
    return HttpResponse(results)

