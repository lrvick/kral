import httplib,pycurl,json
from django.conf import settings
from tasks import ProcessTweet

class Twitter():
    def __init__(self,query):
        self.buffer = ""
        self.stream = pycurl.Curl()
        self.stream.setopt(pycurl.USERPWD, "%s:%s" % (settings.TWITTER_USER, settings.TWITTER_PASS))
        self.stream.setopt(pycurl.URL, "http://stream.twitter.com/1/statuses/filter.json?track=%s" % (query))
        self.stream.setopt(pycurl.WRITEFUNCTION, self.on_receive)
        self.stream.perform()
    def on_receive(self, data):
        self.buffer += data
        if data.endswith("\r\n") and self.buffer.strip():
            ProcessTweet.delay(self.buffer)
            self.buffer = ""

#vim: ai ts=4 sts=4 et sw=4
