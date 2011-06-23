from plugins.facebook import facebook
from celery.task import TaskSet

def stream(queries): 
    query_procs = facebook.delay(queries).get()
    tasks = []
    for query_proc in query_procs:
        tasks.extend(query_proc.subtasks) 
    while tasks:
        current_task = tasks.pop(0)
        if current_task.ready():
            yield current_task.get()
        else:
            tasks.append(current_task)

if __name__ == '__main__':
    for result in stream(['android','bitcoin']):
        print result
