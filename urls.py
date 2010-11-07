from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  (r'^$', 'django.views.generic.simple.direct_to_template', {'template':'base.html'}),
  (r'^admin/', include(admin.site.urls)),
  (r'^twitter/', include('twitter.urls')),
)

# vim: ai ts=4 sts=4 et sw=4
