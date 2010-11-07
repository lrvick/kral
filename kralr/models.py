from django.db import models

class Query(models.Model):
    text = models.CharField(max_length=100,unique=True)
    hits = models.BigIntegerField(default=1)
    last_modified = models.DateTimeField(auto_now=True,auto_now_add=True)

# vim: ai ts=4 sts=4 et sw=4
