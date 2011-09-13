import time
import services
from celery.execute import send_task

all_services = []
for service in services.__all__:
    if service != '__init__':
        all_services.append(service)

def stream(queries,service=None):
    tasks = []
    services = {}
    if service in all_services:
        services[service] = {}
        services[service]['refresh_url'] = {}
    else:
        for service in all_services:
            services[service] = {}
            services[service]['refresh_url'] = {}
    while True:
        for query in queries:
            time.sleep(1)
            for service in services:
                result = send_task('services.%s.feed' % service, [query, services[service]['refresh_url']]).get()
                if result:
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
    for item in stream(['android','bitcoin'],'facebook'):
        print "%s | %s" % (item['service'],item['text'])
