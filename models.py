from django.db import models

class Query(models.Model):
    text = models.CharField(max_length=100,unique=True)
    hits = models.BigIntegerField(default=1)
    last_modified = models.DateTimeField(auto_now=True,auto_now_add=True)

    def __unicode__(self):
       return self.text

class WebLink(models.Model):
    url = models.CharField(unique=True,max_length=4000)
    title = models.CharField(max_length=255,blank=True)
    description = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True,auto_now_add=True)
    total_mentions = models.IntegerField(default=1)
    hits = models.IntegerField(blank=True,default=0)
    type = models.CharField(max_length=100,blank=True)

    def __unicode__(self):
       return self.url

# vim: ai ts=4 sts=4 et sw=4
