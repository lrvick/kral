from django.db import models
from kral.models import *

class FacebookUser(models.Model):
    user_id = models.CharField(max_length=255, help_text="The users ID.")
    name = models.CharField(max_length=255, help_text="The users name.") 
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = "kral"

class FacebookPost(models.Model):
    querys = models.ManyToManyField(Query)
    #Fields are following the Graph API Post properties.
    likes = models.IntegerField(help_text="Number of likes on this post.", null=True, blank=True) #store relationships later
    post_id = models.CharField(max_length=255, help_text="The Post ID", blank=True)
    from_user = models.ForeignKey(FacebookUser, null=True, blank=True, help_text="Information about the user who posted the message.", related_name="fromuser")
    to_users = models.ManyToManyField(FacebookUser, null=True, blank=True, help_text="Profiles mentioned or targeted in this post.", related_name="tousers")
    message = models.TextField(help_text="The message.", blank=True)
    picture = models.URLField(blank=True, help_text="If available, a link to the picture included with this post.", max_length=500)
    link = models.URLField(blank=True, help_text="The link attached to this post.", max_length=500)
    name = models.CharField(max_length=500, blank=True, help_text="The name of the link.")
    caption = models.TextField(blank=True, help_text="The caption of the link.")
    description = models.TextField(help_text="A description of the link.")
    source = models.URLField(blank=True, help_text="A URL to a Flash movie or video file to be embedded within the post.", max_length=500)
    icon = models.URLField(blank=True, help_text="A link to an icon representing the type of this post.", max_length=500)
    attribution = models.CharField(max_length=255, blank=True, help_text="A string indicating which application was used to create this post.")
    created_time = models.DateTimeField(null=True, blank=True)
    updated_time = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=255, help_text="Type of post i.e status, video, link, picture")
    application_name = models.CharField(max_length=500, blank=True, null=True, help_text="The application used to make this post.")
    application_id = models.CharField(max_length=500, blank=True, null=True, help_text="The application's ID.")
    def __unicode__(self):
        return self.post_id
    class Meta:
        app_label = "kral"

# vim: ai ts=4 sts=4 et sw=4
