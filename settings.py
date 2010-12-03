import djcelery,os

from django.conf import settings

djcelery.setup_loader()

USER_AGENT = getattr(settings, "USER_AGENT", "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.7.6) Gecko/20050512 Firefox")

#CELERY_IMPORTS = getattr(settings, "CELERY_IMPORTS", ("kral.plugins.facebook.tasks",))


# vim: ai ts=4 sts=4 et sw=4
