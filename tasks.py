import base64
import ewrl
import pickle
import urllib
import urllib2
from celery.decorators import task
from eventlet.timeout import Timeout
from kral import settings
from kral.utils import cache
from plugins import *

@task
def url_process(url,query,n=1,original_url=None,**kwargs):
    logger = url_process.get_logger(**kwargs)
    all_links_cache_name = "alllinks_%s" % str(query.replace(' ',''));
    expanded_cache_name = "expanded_%s" % base64.b64encode(url)
    url_expanded = cache.get(expanded_cache_name)
    if not url_expanded:
        with Timeout(10, False) as timeout:
            try:
                url_expanded = ewrl.url_expand(url)
            except Timeout:
                logger.error("Timed out expanding URL: %s" % url)
                url_expanded = url
            except Exception, e:
                logger.error(e)
                url_expanded = url
                cache.set(expanded_cache_name,url_expanded)
    url_mentions = 300
    title_cache_name = "title_%s" % base64.b64encode(url_expanded)
    url_title = cache.get(title_cache_name)
    if not url_title:
        with Timeout(10, False) as timeout:
            try:
                url_title, url_feed = ewrl.url_data(url_expanded)
                if url_feed is not None:
                    #TODO: this was our only dependency on django models. lets re-think this.
                    #feed = Feed(href=url_feed,title=url_title)
                    #feed.save()
                    print 'saved new feed: %s' % url_feed
            except Timeout:
                logger.error("Timed out fetching title for URL: %s" % url_expanded)
                url_title = 'No Title'
            except Exception, e:
                logger.error(e)
                url_title = 'No Title'
                cache.set(title_cache_name,url_title)
    mentions_cache_name = "mentions_%s" % base64.b64encode(url_expanded)
    url_mentions_cached = cache.get(mentions_cache_name)
    if not url_mentions_cached:
        url_mentions = 1
    else:
        url_mentions = int(url_mentions_cached) + 1
    cache.set(mentions_cache_name,url_mentions)
    post_info = {'service':'links','href':url_expanded,'count':url_mentions,'title':url_title}
    try:
       links = pickle.loads(cache.get(all_links_cache_name))
    except:
        links = []
    new_link = True
    for link in links:
        if link['href'] == url_expanded:
            link['count'] += 1
            new_link = False
    if new_link:
        links.append(post_info)
    links = sorted(links, key=lambda link: link['count'],reverse=True)
    cache.set(all_links_cache_name, pickle.dumps(links))
    push_data(post_info,queue=query)

#vim: ai ts=4 sts=4 et sw=4
