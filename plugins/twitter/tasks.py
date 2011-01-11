import urllib2,urlparse,json,time,re,sys,time,os,socket,base64
from celery.task.base import PeriodicTask,Task
from celery.signals import worker_ready
from django.conf import settings
from models import *
from kral.models import *
from tasks import *
from kral.tasks import *
from celery.registry import tasks
from celery.execute import send_task

class Twitter(Task):
    def run(self, querys, **kwargs):
        logger = self.get_logger(**kwargs)
        self.query_post = str("track="+",".join([q.text for q in querys]))
        self.request = urllib2.Request('http://stream.twitter.com/1/statuses/filter.json',self.query_post)
        self.auth = base64.b64encode('%s:%s' % (settings.TWITTER_USER, settings.TWITTER_PASS))
        self.request.add_header('Authorization', "basic %s" % self.auth)
        try:
            self.stream = urllib2.urlopen(self.request)
        except Exception,e:
            if e.code == 420:
                logger.info("Twitter connection closed")
            else:
                logger.error("Invalid/null response from server: %s" % (e))
            return False
        for tweet in self.stream:
            ProcessTweet.delay(tweet, querys)

class ProcessTweet(Task):
    def run(self, data, querys, **kwargs):
        logger = self.get_logger(**kwargs)
        content = json.loads(data)
        user_id = content["user"].get('id_str', None)
        urls = content['entities']['urls']
        time_format = "%a %b %d %H:%M:%S +0000 %Y"
        if user_id:
            twitter_user, created = TwitterUser.objects.get_or_create(
                user_id = user_id,#unique
                defaults = {
                    "user_name" : content["user"]["screen_name"],
                    "real_name" : content["user"]["name"],
                    #location = content["user"]["location"],
                    "avatar" : content["user"]["profile_image_url"],
                    "date" : datetime.datetime.fromtimestamp(time.mktime(time.strptime(content["user"]["created_at"],time_format))),
                    "language" : content["user"]["lang"],
                    "total_tweets" : content["user"]["statuses_count"],
                    #time_zone = content["user"]["time_zone"],
                    "listed" : content["user"]["listed_count"],
                    "following" : content["user"]["friends_count"],
                    "followers" : content["user"]["followers_count"],
                    "geo_enabled" : content["user"]["geo_enabled"],
                    "contributors_enabled" : content["user"]["contributors_enabled"],
                    #utc_offset = content["user"]["utc_offset"],
                }
            )
            #twitter_user.save()
            logger.debug("Saved/Updated profile for Twitter user %s" % (content["user"]["screen_name"]))
            try:
                twitter_tweet, created = TwitterTweet.objects.get_or_create(
                    tweet_id = content["id_str"], #unique
                    defaults = {
                        "date": datetime.datetime.fromtimestamp(time.mktime(time.strptime(content["created_at"],time_format))),
                        "user_id" : TwitterUser.objects.get(user_id=content["user"]["id_str"]),
                        "text" : content["text"],
                        #place = content["user"]["place"],
                        "truncated" : content['truncated'], 
                        "geo" : content["user"]["location"],
                        "contributors" : content["contributors"],
                        #retweeted = content['retweeted'], 
                        #irt_status_id = content['in_reply_to_status_id'],
                        #irt_status_name = content['in_reply_to_status_name'],
                        #retweet_count = content['retweet_count'], 
                        #geo = content['geo'],
                    }
                )
                #twitter_tweet.save()
                for query in [query.text.lower() for query in querys]:
                    if query in twitter_tweet.text.lower():
                        qobj = Query.objects.get(text__iexact=query)
                        twitter_tweet.querys.add(qobj)
                        for url in urls: 
                            if url['expanded_url']:
                                send_task("kral.tasks.ExpandURL", [url['expanded_url'],query])
                            else:
                                send_task("kral.tasks.ExpandURL", [url['url'],query])
                        logger.debug("Added relation for tweet %s to %s" % (content['id_str'], qobj))
            except Exception, e:
                logger.error("Unable to save tweet %s - %s" % (content["id_str"],e))

#vim: ai ts=5 sts=4 et sw=4
