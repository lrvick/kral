import httplib,urlparse,pycurl,json,time,re,sys,time,datetime,os,threading
from celery.task.base import Task
from django.conf import settings
from models import *
from kral.models import *
from celery.registry import tasks

class ProcessTweet(Task):
    def run(self, data, **kwargs):
        logger = self.get_logger(**kwargs)
        content = json.loads(data)
        user_id = content["user"].get('id_str', None)
        urls = content['entities']['urls']
        if user_id is not None:
            for url in urls: #this sin't defined at this point
                if url['expanded_url']:
                    ExpandURL.delay(url['expanded_url'])
                else:
                    ExpandURL.delay(url['url'])
            try:
                twitter_user = TwitterUser.objects.get(user_id=user_id)
                twitter_user.total_tweets = content["user"]["statuses_count"],
                twitter_user.listed = content["user"]["listed_count"],
                twitter_user.following = content["user"]["friends_count"],
                twitter_user.followers = content["user"]["followers_count"],
                twitter_user.save()
                logger.info("Updated profile for Twitter user %s" % (content["user"]["screen_name"]))
            except:
                twitter_user = TwitterUser (
                    user_id = user_id,
                    user_name = content["user"]["screen_name"],
                    real_name = content["user"]["name"],
                    #location = content["user"]["location"],
                    avatar = content["user"]["profile_image_url"],
                    date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(content["user"]["created_at"], '%a %b %d %H:%M:%S +0000 %Y'))),
                    language = content["user"]["lang"],
                    total_tweets = content["user"]["statuses_count"],
                    #time_zone = content["user"]["time_zone"],
                    listed = content["user"]["listed_count"],
                    following = content["user"]["friends_count"],
                    followers = content["user"]["followers_count"],
                    geo_enabled = content["user"]["geo_enabled"],
                    contributors_enabled = content["user"]["contributors_enabled"],
                    #utc_offset = content["user"]["utc_offset"],
                )
                twitter_user.save()
                logger.info("Saved new profile Twitter user %s" % (content["user"]["screen_name"]))
            try:
                twitter_user = TwitterUser.objects.get(user_id=user_id)
                twitter_tweet = TwitterTweet (
                    date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(content["created_at"], '%a %b %d %H:%M:%S +0000 %Y'))),
                    tweet_id = content["id_str"],
                    user_id = TwitterUser.objects.get(user_id=content["user"]["id_str"]),
                    text = content["text"],
                    #place = content["user"]["place"],
                    truncated = content['truncated'], 
                    geo = content["user"]["location"],
                    contributors = content["contributors"],
                    #retweeted = content['retweeted'], 
                    #irt_status_id = content['in_reply_to_status_id'],
                    #irt_status_name = content['in_reply_to_status_name'],
                    #retweet_count = content['retweet_count'], 
                    #geo = content['geo'], 
                )
                twitter_tweet.save()
                logger.info("Saved new tweet: %s" % (content["id_str"]))
                return True
            except:
                logger.info("ERROR - Unable to save tweet %s" % (content["id_str"]))

class ExpandURL(Task):
    def run(self,url,n=1,original_url=None,**kwargs):
        if n == 1:
            original_url = url
        logger = self.get_logger(**kwargs)
        headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"}
        parsed_url = urlparse.urlsplit(url)
        request = urlparse.urlunsplit(('', '', parsed_url.path, parsed_url.query, parsed_url.fragment))
        connection = httplib.HTTPConnection(parsed_url.netloc)
        try : 
            connection.request('HEAD', request, "", headers)
            response = connection.getresponse()
        except:
            return "Connection request failed"
        current_url = response.getheader('Location')
        n += 1
        if n > 3 or current_url == None:
            ProcessURL.delay(url)
            logger.info("Expanded URL \"%s\" to \"%s\"" % (original_url,url))
            return True
        else:
            ExpandURL.delay(current_url, n)

class ProcessURL(Task):
    def run(self,url,**kwargs):
        logger = self.get_logger(**kwargs)
        try:
            old_link = WebLink.objects.get(url=url)
            old_link.total_mentions += 1
            old_link.save()
            logger.info("Recorded mention of known URL: \"%s\"" % (url))
        except:
            weblink = WebLink(
                url = url,
            )
            weblink.save()
            logger.info("Added record for new URL: \"%s\"" % (url))
            return True

tasks.register(ProcessTweet)
tasks.register(ProcessURL)
tasks.register(ExpandURL)

#vim: ai ts=4 sts=4 et sw=4
