import time,feedparser,re  #search - what is this?
from datetime import datetime
from django.utils.encoding import smart_unicode
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from twitter.models import TwitterTweet,TwitterUser

def twitter_search(request):
    query = request.GET['q']
    twitter_feed = feedparser.parse("http://search.twitter.com/search.atom?q="+query)
    existing_tweets = TwitterTweet.objects.filter(text__icontains=query)
    for entry in twitter_feed['entries']:
        time = entry.published_parsed
        date = datetime(time.tm_year, time.tm_mon, time.tm_mday, time.tm_hour, time.tm_min, time.tm_sec)
        link = entry.links[0].href
        avatar = entry.links[1].href
        user_name = entry.author_detail.name.split()[0]
        text = re.sub(r'^\w+:\s', '', entry['title'])
        tweet = TwitterTweet(
		  text = text,
		  date = date,
		  link = link,
		  avatar = avatar,
		)
        user = TwitterUser(
          user_name = user_name,
        )
        try:
          #return u'%s - %s' % (user_name, text[:20])
          old_tweet = existing_tweets.get(link=link)
        except TwitterTweet.DoesNotExist:
          tweet.save()    
    tweets = TwitterTweet.objects.filter(text__icontains=query).order_by('-published')

# vim: ai ts=4 sts=4 et sw=4
