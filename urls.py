from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^$', 'django.views.generic.simple.direct_to_template', {'template':'base.html'}),
  (r'^.*$', include('kral.urls')),
)

# vim: ai ts=4 sts=4 et sw=4
