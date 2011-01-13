import urllib2,json,base64,stomp
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
            post_info = {
                "service" : 'twitter',
                "user" : content["user"]["screen_name"],
                "message" : content["text"],
                "picture" : content['user']["profile_image_url"],
            }
            conn = stomp.Connection()
            conn.start()
            conn.connect()
            conn.send(json.dumps(post_info), destination='/messages')

#vim: ai ts=5 sts=4 et sw=4
