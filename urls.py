from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
  (r'^(?P<plugin>\w+)/(?P<query>\w+).(?P<format>\w+)$', serialize_model),
  (r'^/feeds/(?P<cache_name>\w+).json$', fetch_cache),
)

# vim: ai ts=4 sts=4 et sw=4
