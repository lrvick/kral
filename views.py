import datetime,json,pickle,redis
from django.http import HttpResponse, Http404
from django.conf import settings
from celery.execute import send_task
from kombu import BrokerConnection, Exchange, Producer

cache = redis.Redis(host='localhost', port=6379, db=1)

def fetch_cache(request,service,query):
    cache_data = []
    if service == "all":
        for service in settings.KRAL_PLUGINS:
            cache_name = "%s_%s" % (service.lower(), query)
            cache_data += pickle.loads(cache.get(cache_name))
    elif service == "links":
        cache_name = "alllinks_%s" % query
        cache_data = pickle.loads(cache.get(cache_name))[:30]
    else:
        cache_name = "%s_%s" % (service,query)
        cache_data = pickle.loads(cache.get(cache_name))
    return HttpResponse(json.dumps(cache_data))

def fetch_queries(**kwargs):
    slots = getattr(settings, 'KRAL_SLOTS', 1)
    try:
        cached_queries = pickle.loads(cache.get('KRAL_QUERIES'))[:slots]
        queries = []
        for query in cached_queries:
            queries.append(query.replace(' ','_'))
    except Exception:
        settings_queries = getattr(settings, 'KRAL_QUERIES', ['foo','bar','null'])
        queries = []
        for query in settings_queries:
            queries.append(query.replace(' ','_'))
        cache.set('KRAL_QUERIES',pickle.dumps(queries))
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
    cache.set(cache_name, pickle.dumps(merged[-50:]))
    cache.set(default_cache_name, pickle.dumps(default_merged[-50:]))
    exchange_send(data,queue)
    exchange_send(data,'default')
    if data.get('links',None):
        for link in data['links']:
            send_task("kral.tasks.url_expand", [link['href'], queue])

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
    cache.set('KRAL_QUERIES',pickle.dumps(queries))


