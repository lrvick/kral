from django.db import models

class Feed(models.Model):
    title = models.CharField(max_length=100, unique=True)
    href = models.URLField(verify_exists=True)
    last_scan = models.DateTimeField(auto_now=True, auto_now_add=True)

class FeedTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

class FeedItem(models.Model):
    title = models.CharField(max_length=255, unique=False)
    feed = models.ForeignKey(Feed)
    pub_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    description = models.TextField()
    href = models.URLField(verify_exists=False,unique=True)
    tags = models.ManyToManyField(FeedTag)
