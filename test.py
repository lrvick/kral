#__all__ = ['Foo']

#class Foo(object):
#    def __init__(self):
#        self.x = 3
import celeryconfig

from celery.execute import send_task

result = send_task('kral.plugins.facebook.facebook',['android'])

print result.get()
