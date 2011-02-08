import datetime,json,pickle
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core import serializers
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.middleware.csrf import get_token
from kombu import BrokerConnection, Exchange, Producer

def index(request,query='default'):
    try:
        query = request.REQUEST['query']
        add_query_result = add_query(query)
    except:
        query = query
    query = query.replace(' ','_')
    queries = fetch_queries()
    all_queries = {}
    for this_query in queries[:5]:
        all_queries[this_query] = this_query.replace('_',' ')
    print(query)
    return render_to_response('index.html', {
        "orbited_server": settings.ORBITED_SERVER,
        "orbited_port": settings.ORBITED_PORT,
        "orbited_stomp_port": settings.ORBITED_STOMP_PORT,
        "all_queries": all_queries,
        "query": query,
        "csrf_token": get_token(request),
    })

def fetch_cache(request,service,query):
    cache_name = "%s_%s" % (service,query);
    cache_data = pickle.loads(cache.get(cache_name))
    return HttpResponse(json.dumps(cache_data))

def fetch_queries(**kwargs):
    slots = getattr(settings, 'KRAL_SLOTS', 1)
    try:
        settings_queries = pickle.loads(cache.get('KRAL_QUERIES'))[:slots]
        queries = []
        for query in settings_queries:
            queries.append(query.replace(' ','_'))
    except Exception:
        queries = getattr(settings, 'KRAL_QUERIES', ['foo','bar','null'])
        cache.set('KRAL_QUERIES',pickle.dumps(queries),31556926)
    return queries

def exchange_send(data,exchange):
    try:
        connection = BrokerConnection()
        channel = connection.channel()
        producer = Producer(channel, Exchange(exchange, type="fanout"))
        producer.publish(data)
        channel.close()
        connection.close()
    except Exception, error:
        print(error)

def push_data(data,queue):
    cache_name = "%s_%s" % (str(data['service']),str(queue.replace(' ','')));
    default_cache_name = "%s_default" % str(data['service']);
    try:
        last_data = pickle.loads(cache.get(cache_name))
        merged = last_data + [data]
        default_last_data = pickle.loads(cache.get(default_cache_name))
        default_merged = default_last_data + [data]
    except Exception, error:
        merged = [data]
        default_merged = [data]
    cache.set(cache_name, pickle.dumps(merged[-50:]),31556926)
    cache.set(default_cache_name, pickle.dumps(default_merged[-50:]),31556926)
    exchange_send(data,queue)
    exchange_send(data,'default')

def add_query(query):
    query = query.lower()
    queries = fetch_queries()
    result = True
    slots = getattr(settings, 'KRAL_SLOTS', 1)
    if query in queries:
        queries.remove(query)
    else:
        try:
            connection = BrokerConnection();
            channel = connection.channel();
            Exchange(query, type="fanout")(channel).declare()
            print('Exchange declared for: %s' % query)
        except Exception,error:
            print(error)
    queries.insert(0,query)
    queries = queries[:slots]
    cache.set('KRAL_QUERIES',pickle.dumps(queries),31556926)
