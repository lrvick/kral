from django.conf.urls.defaults import *

urlpatterns = patterns('kral.views',
  (r'^/listener/(?P<plugin>\w+)$)','route_listener')),
)

# vim: ai ts=4 sts=4 et sw=4
