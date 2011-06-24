import time
import settings
from plugins.facebook import facebook
from celery.task import TaskSet
from celery.execute import send_task

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
                result = send_task('plugins.%s.%s' % (service,service),[query, services[service]['refresh_url']]).get()
                services[service]['refresh_url'] = result[0] 
                taskset = result[1]
                tasks.extend(taskset.subtasks) 
                while tasks:
                    current_task = tasks.pop(0)
                    if current_task.ready():
                        post = current_task.get()
                        if post:
                            yield post
                    else:
                        tasks.append(current_task)

if __name__ == '__main__':
    for result in stream(['android','bitcoin']):
        print result['service'],result['text']
