from django.db import models

class FacebookUser(models.Model):
    user_id = models.CharField(max_length=255, help_text="The users ID.")
    name = models.CharField(max_length=255, help_text="The users name.") 
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "kral"

#class FacebookComment(models.Model):
#   comment_id = models.CharField(max_length=255, help_text="The comments id.")    
#   from = models.ForeignKey(FacebookUser, help_text="The user who posted this comment.)"
#   message = models.TextField()
#   created_time = models.DateTimeField()


#   def __unicode__(self):
#       return self.message[:20]


class FacebookPost(models.Model):
    #Fields are following the Graph API Post properties.
    likes = models.IntegerField(help_text="Number of likes on this post.", null=True, blank=True)
    post_id = models.CharField(max_length=255, help_text="The Post ID", blank=True)
    from_user = models.ForeignKey(FacebookUser, null=True, blank=True, help_text="Information about the user who posted the message.", related_name="fromuser")
    to_users = models.ManyToManyField(FacebookUser, null=True, blank=True, help_text="Profiles mentioned or targeted in this post.", related_name="tousers")
    message = models.TextField(help_text="The message.", blank=True)
    picture_link = models.URLField(blank=True, help_text="If available, a link to the picture included with this post.")
    link = models.URLField(blank=True, help_text="The link attached to this post.")
    name = models.CharField(max_length=255, blank=True, help_text="The name of the link.")
    caption = models.CharField(max_length=255, blank=True, help_text="The caption of the link.")
    description = models.TextField(help_text="A description of the link.")
    source = models.URLField(blank=True, help_text="A URL to a Flash movie or video file to be embedded within the post.")
    icon = models.URLField(blank=True, help_text="A link to an icon representing the type of this post.")
    attribution = models.CharField(max_length=255, blank=True, help_text="A string indicating which application was used to create this post.")
   
    properties_name = models.CharField(max_length=255, blank=True)
    properties_href = models.URLField(blank=True)
    properties_text = models.TextField(blank=True)

    #actions NOTE: not sure if this is relevant to store
    #privacy NOTE: same as above
    
    created_time = models.DateTimeField(null=True, blank=True)
    updated_time = models.DateTimeField(null=True, blank=True)
    #targeting NOTE: needs manage_pages permission not sure if this is publically available 

    #connection_likes = models.ManyToManyField(FacebookUser, help_text="The people who liked this post.") 
    #connection_comments = models.ManyToManyField(FacebookComment, help_text="Comments made on this post.)"

    post_type = models.CharField(max_length=255, help_text="Type of post i.e status, video, link, picture")

    def __unicode__(self):
        return self.message[:20]

    class Meta:
        app_label = "kral"


# vim: ai ts=4 sts=4 et sw=4
