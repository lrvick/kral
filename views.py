import datetime,json,pickle
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core import serializers
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.middleware.csrf import get_token
from kombu import BrokerConnection, Exchange, Producer

def index(request,query=None):
    queries = fetch_queries()
    try:
        query = request.REQUEST['query']
        queries = add_query(query,queries)
    except:
        query = query
    return render_to_response('index.html', {
        "orbited_server": settings.ORBITED_SERVER,
        "orbited_port": settings.ORBITED_PORT,
        "orbited_stomp_port": settings.ORBITED_STOMP_PORT,
        "all_queries": queries[:5],
        "query": query,
        "csrf_token": get_token(request),
    })

def push_data(data,queue):
    cache_name = "%s_%s" % (str(data['service']),str(queue));
    try:
        last_data = pickle.loads(cache.get(cache_name))
        merged = last_data + [data]
    except:  
        merged = [data]
    cache.set(cache_name, pickle.dumps(merged[-50:]),31556926) 
    connection = BrokerConnection()
    channel = connection.channel()
    producer = Producer(channel, Exchange(queue, type="fanout"))
    producer.publish(data)
    channel.close()
    connection.close()

def fetch_cache(request,service,query):
    cache_name = "%s_%s" % (service,query);
    cache_data = pickle.loads(cache.get(cache_name))
    return HttpResponse(json.dumps(cache_data))

def fetch_queries(**kwargs):
    slots = getattr(settings, 'KRAL_SLOTS', 1)
    try:
        queries = pickle.loads(cache.get('KRAL_QUERIES'))[:slots]
    except Exception:
        queries = getattr(settings, 'KRAL_QUERIES', ['foo','bar','null'])
        cache.set('KRAL_QUERIES',pickle.dumps(queries),31556926)
    return queries

def add_query(query,queries):
    slots = getattr(settings, 'KRAL_SLOTS', 1)
    if query in queries:
        queries.remove(query)
    queries.insert(0,query)
    queries = queries[:slots]
    cache.set('KRAL_QUERIES',pickle.dumps(queries),31556926)
    return queries
    
