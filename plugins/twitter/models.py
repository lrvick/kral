from django.db import models
from kral.models import *

# -- Twitter variable defs --
# user_name      | Do not trust, users can change it
# location  | Users location listed in profile
# user_id        | Trust this, users can never change it
# tweet_id       | ID of a given tweet
# real_name      | Users real name. Don't trust this, users can change it
# description    | description of a user by itself
# text           | text of actual tweet 
# date           | date user/tweet was created/posted
# avatar         | href linking directly to users avatar
# language       | 2 char language code for user/tweet
# source         | Application used to create tweet
# link           | Direct href to origional tweet
# irt_status_id  | ID of tweet this is tweet is responding to
# irt_user_id    | ID of the user whos tweet this is tweet is responding to
# irt_user_name  | Name of the user whos tweet this is tweet is responding to
# retweet_count  | Number of times this tweet has been retweeted
# sentiment      | 0/P/N for neutral/positive/negative sentiment
# following      | Number of users a user is following
# followers      | Number of users following this user
# listed         | Number of lists including this user
# total_tweets   | Total number of tweets a user has posted
# last_updated   | last time this particular users info was updated
# geo_enabled    | Indicates user support for GPS tracking on tweets

SENTIMENT_CHOICES = (
        ('0','Neutral'),
        ('P','Positive'),
        ('N','Negative'),
)

class TwitterUser(models.Model):
    user_id = models.BigIntegerField(primary_key=True,unique=True) 
    user_name = models.CharField(max_length=100,blank=True) 
    real_name = models.CharField(max_length=100,blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100,blank=True)
    avatar = models.URLField(blank=True) 
    date = models.DateTimeField(blank=True)
    language = models.CharField(max_length=2)
    total_tweets = models.IntegerField(blank=True)
    time_zone = models.CharField(max_length=100,blank=True)
    listed = models.IntegerField(blank=True,null=True)
    following = models.IntegerField(blank=True)
    followers = models.IntegerField(blank=True)
    geo_enabled = models.BooleanField()
    contributors_enabled = models.BooleanField()
    utc_offset = models.CharField(max_length=20,blank=True)
    last_modified = models.DateTimeField(auto_now=True,auto_now_add=True)
    def __unicode__(self):
        return self.user_name
    class Meta:
        app_label = 'kral'

class TwitterTweet(models.Model):
    querys = models.ManyToManyField(Query)
    user_id = models.ForeignKey(TwitterUser)
    contributors = models.TextField(blank=True,null=True)
    tweet_id = models.BigIntegerField(primary_key=True,unique=True) 
    geo = models.CharField(max_length=250,blank=True,null=True)
    place = models.CharField(max_length=100,blank=True,null=True)
    text = models.TextField()
    date = models.DateTimeField()
    language = models.CharField(max_length=2,default='en')
    source = models.CharField(max_length=100,blank=True,null=True)
    irt_status_id = models.BigIntegerField(blank=True,null=True)
    irt_user_id = models.BigIntegerField(blank=True,null=True)
    irt_user_name = models.CharField(max_length=100,unique=True,blank=True,null=True)
    retweet_count = models.BigIntegerField(blank=True,null=True)
    sentiment = models.CharField(max_length=1,default='0',choices=SENTIMENT_CHOICES)
    truncated = models.BooleanField(default=0)
    last_modified = models.DateTimeField(auto_now=True,auto_now_add=True)
    def __unicode__(self):
        return self.text[:20]
    class Meta:
        app_label = 'kral'

# vim: ai ts=4 sts=4 et sw=4
