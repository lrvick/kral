import httplib,urlparse,pycurl,json,time,re,sys,time,datetime,os
from django.conf import settings
from models import *
from kral.models import *

QUERY="love"

class Twitter(object):
    def __init__(self):
        self.buffer = ""
        self.stream = pycurl.Curl()
        self.stream.setopt(pycurl.USERPWD, "%s:%s" % (settings.TWITTER_USER, settings.TWITTER_PASS))
        self.stream.setopt(pycurl.URL, "http://stream.twitter.com/1/statuses/filter.json?track=%s" % (QUERY))
        self.stream.setopt(pycurl.WRITEFUNCTION, self.on_receive)
        self.stream.perform()
    def on_receive(self, data):
        self.buffer += data
        if data.endswith("\r\n") and self.buffer.strip():
            content = json.loads(self.buffer)
            self.buffer = ""
            user_id = content["user"].get('id_str', None)
            if user_id is not None:
                print "--------------------------------------"
                print content["text"].encode( "utf-8" )
                print content["user"]["id_str"]
                urls = content['entities']['urls']
                try:
                    twitter_user = TwitterUser.objects.get(user_id=user_id)
                    twitter_user.total_tweets = content["user"]["statuses_count"],
                    twitter_user.listed = content["user"]["listed_count"],
                    twitter_user.following = content["user"]["friends_count"],
                    twitter_user.followers = content["user"]["followers_count"],
                    twitter_user.save()
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
                def expand_url(url, n=1):
                    headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox"}
                    parsed_url = urlparse.urlsplit(url)
                    request = urlparse.urlunsplit(('', '', parsed_url.path, parsed_url.query, parsed_url.fragment))
                    connection = httplib.HTTPConnection(parsed_url.netloc)
                    try : 
                        connection.request('HEAD', request, "", headers)
                        response = connection.getresponse()
                    except:
                        #return None
                        #return exception
                        return "Connection request failed"
                    current_url = response.getheader('Location')
                    n += 1
                    if n > 3:
                        return url
                    elif current_url == None:
                        return url
                    else:
                        url = current_url
                        return expand_url(url, n)

                for url in urls:
                    if url['expanded_url']:
                        check_url = url['expanded_url']
                    else:
                        check_url = url['url']
                    url = expand_url(check_url)
                    try:
                        old_link = WebLink.objects.get(url=url)
                        old_link.total_mentions += 1
                        old_link.save()
                    except:
                        weblink = WebLink(
                            url = url,
                        )
                        weblink.save()

#vim: ai ts=4 sts=4 et sw=4
