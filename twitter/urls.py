from django.conf.urls.defaults import *
from twitter.views import *

urlpatterns = patterns('', 
   url(r'^$', twitter_search, name='search'), 
)

