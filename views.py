import datetime,json,pickle
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core import serializers
from django.core.cache import cache
from kombu import BrokerConnection, Exchange, Producer

def push_data(data,queue):
    cache_name = data['service'];
    try:
        last_data = pickle.loads(cache.get(cache_name))
        merged = last_data + [data]
    except:  
        merged = [data]
    cache.set(cache_name, pickle.dumps(merged[-50:])) 
    connection = BrokerConnection()
    channel = connection.channel()
    producer = Producer(channel, Exchange("messages", type="fanout"))
    producer.publish(data)
    channel.close()
    connection.close()

def fetch_cache(request,cache_name):
    cache_data = pickle.loads(cache.get(cache_name))
    return HttpResponse(json.dumps(cache_data))
