import os
import time
import sys
import settings

p = os.path.realpath(os.path.dirname(__file__))
sys.path.append(p)

from celery.execute import send_task

os.environ['CELERY_CONFIG_MODULE'] = 'celeryconfig'

from celery import registry

print registry.tasks

def stream(queries):
    while True:
        tasks = []
        services = {}
        for query in queries:
            time.sleep(1)
            for service in settings.KRAL_PLUGINS:
                if service not in services:
                    services[service] = {}
                    services[service]['refresh_url'] = None
                result = send_task('services.%s.feed' % service, [query, services[service]['refresh_url']]).get()
                if result:
                    print result[0]
                    services[service]['refresh_url'] = result[0]
                    taskset = result[1]
                    tasks.extend(taskset.subtasks)
                    while tasks:
                        current_task = tasks.pop(0)
                        if current_task.ready():
                            post = current_task.get()
                            if post is not None:
                                yield post
                        else:
                            tasks.append(current_task)

if __name__ == '__main__':
    for item in stream(['android','bitcoin']):
        print "%s | %s" % (item['service'],item['text'])
