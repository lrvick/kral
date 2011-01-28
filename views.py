import datetime,stomp,json,pickle
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core import serializers
from django.core.cache import cache
from kombu import BrokerConnection, Exchange, Producer

def push_data(data,queue):
    if not cache.has_key('messages_buffer'):
        merged = [str(data)]
    else:  
        last_data = pickle.loads(cache.get('messages_buffer'))
        merged = last_data + [str(data)]
    cache.set('messages_buffer', pickle.dumps(merged[-50:])) 
    connection = BrokerConnection()
    channel = connection.channel()
    producer = Producer(channel, Exchange("messages", type="fanout"))
    producer.publish(data)
    channel.close()
    connection.close()

def fetch_cache(request):
    cache_data = pickle.loads(cache.get('messages_buffer'))
    return HttpResponse(cache_data)
