import httplib,urlparse,re,sys,os,datetime,djcelery,pickle,urllib2,base64,urllib,redis
from django.conf import settings
from celery.task.control import inspect
from celery.decorators import task
from celery.signals import worker_ready,beat_init
from celery.execute import send_task
from kral.views import push_data
from eventlet.timeout import Timeout

cache = redis.Redis(host='localhost', port=6379, db=1)

ALLPLUGINS = []
if not hasattr(settings, "KRAL_PLUGINS"): 
    for plugin in [x.lower() for x in os.listdir(os.path.join(settings.PROJECT_PATH,'kral/plugins')) if not x.startswith('__')]:
        __import__('kral.plugins.'+plugin+'.tasks', fromlist=["*"])
        ALLPLUGINS.append(plugin.title())
else:
    for plugin in settings.KRAL_PLUGINS:
        plugin = plugin.lower()
        try:
            __import__('kral.plugins.'+plugin+'.tasks', fromlist=["*"])
        except ImportError:
            raise ImportError('Module %s does not exist.' % plugin)

def kral_init(**kwargs):
    from djcelery.models import PeriodicTask,PeriodicTasks
    PeriodicTask.objects.all().delete()
    PeriodicTasks.objects.all().delete()
    task_cache = redis.Redis(host='localhost', port=6379, db=0)
    task_cache.flushdb()
beat_init.connect(kral_init) 

def fixurl(url):
    domain, query = urllib.splitquery(url)
    new_url = None
    if query:
        query = re.sub('utm_(source|medium|campaign)\=([^&]+)&?', '', query)
        new_url = urlparse.urljoin(domain, "?"+query)
    else:
        new_url = domain 
    return new_url

@task
def url_expand(url,query,n=1,original_url=None,**kwargs):
    if n == 1:
        original_url = url
    logger = url_expand.get_logger(**kwargs)
    headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"}
    parsed_url = urlparse.urlsplit(url)
    request = urlparse.urlunsplit(('', '', parsed_url.path, parsed_url.query, parsed_url.fragment))
    response = None
    current_url = None
    try:
        connection = httplib.HTTPConnection(parsed_url.netloc)
    except httplib.InvalidURL:
        logger.error("Unable to expand Invalid URL: %s" % url)
        return False
    with Timeout(5, False) as timeout:
        try: 
            connection.request('HEAD', request, "", headers)
            response = connection.getresponse()
        except Exception, e:
            logger.error(e)
        except Timeout:
            logger.info("URL Timed out: %s" % url)
    if response:
        location = response.getheader('Location')
        if location:
            content_header = response.getheader('Content-Type');
            if content_header:
                encoding = content_header.split('charset=')[-1]
                try:
                    current_url = unicode(location, encoding)
                except LookupError:
                    pass
    n += 1
    if n > 3 or current_url == None:
        cache_name = "alllinks_%s" % str(query.replace(' ',''));
        try:
            links = pickle.loads(cache.get(cache_name))
        except:
            links = []
        url = fixurl(url)
        new_link = False
        url_cache_name = base64.b64encode(url)[:250]
        cached_title = cache.get(url_cache_name)
        title = None
        if cached_title:
            title = base64.b64decode(cached_title)
            unicode(title,'utf8')
        else:
            title = None
        for link in links:
            if link['href'] == url:
                link['count'] += 1
                if link['count'] > 1:
                    if  title:
                        link['title'] = title
                    else: 
                        url_title.delay(url)
                new_link = True
                post_info = link
        if new_link == False:
            post_info = {'service':'links','href':url,'count':1,'title':title}
            links.append(post_info)
        links = sorted(links, key=lambda link: link['count'],reverse=True)
        cache.set(cache_name, pickle.dumps(links))
        push_data(post_info,queue=query)
    else:
        url_expand.delay(current_url,query,n,original_url)

@task
def url_title(url,**kwargs):
    logger = url_expand.get_logger(**kwargs)
    cache_name = base64.b64encode(url)[:250]
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
        data = response.read()
    except urllib2.HTTPError:
        data = None
    except urllib2.URLError:
        data = None
    except httplib.BadStatusLine:
        data = None
    except httplib.InvalidURL:
        data = None
    except httplib.IncompleteRead:
        data = None
    except ValueError:
        data = None
    if data:
        if '<title>' in data:
            headers = response.info()
            content_type = headers.get('content-type',None)
            if content_type:
                raw_encoding = content_type.split('charset=')[-1]
                if 'text/html' in raw_encoding:
                    encoding = 'unicode-escape'
                else:
                    encoding = raw_encoding
                title_search = re.search('(?<=<title>).*(?=<\/title>)',data)
                if title_search:
                    try:
                        title = unicode(title_search.group(0),encoding)
                        #print(encoding,url,title[:20])
                        cache.set(cache_name,base64.b64encode(title.encode('utf8')))
                    except Exception, e:
                        print(e)
                        title = None
            else:
                loggger.error("Unknown content type for URL: %s" % url)

#vim: ai ts=4 sts=4 et sw=4
