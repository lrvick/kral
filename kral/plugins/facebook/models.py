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
    status_id = models.CharField(max_length=255)
    from_user = models.ForeignKey(FacebookUser, null=True, blank=True)
    #to_user = models.ForeignKey(FacebookUser, null=True, blank=True)
    message = models.TextField()
    created_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    type = models.CharField(max_length=255)
    attribution = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.message[:20]

    class Meta:
        app_label = "kral"


# vim: ai ts=4 sts=4 et sw=4
