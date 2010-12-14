from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
  (r'^(?P<model>\w+)/(?P<query>\w+).(?P<format>\w+)$', serialize_model),
)

# vim: ai ts=4 sts=4 et sw=4
