from django.db import models

#TODO: store likes and comments on each status.

class FacebookUser(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=255) 
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "kral"

class FacebookStatus(models.Model):
    status_id = models.IntegerField()
    from_user = models.ForeignKey(FacebookUser)
    message = models.TextField()
    updated_time = models.DateTimeField()
    
    def __unicode__(self):
        return message[:20]

    class Meta:
        app_label = "kral"


# vim: ai ts=4 sts=4 et sw=4
