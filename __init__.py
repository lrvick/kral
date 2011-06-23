from plugins.facebook import facebook
from celery.task import TaskSet

def stream(queries): 
    results = TaskSet(facebook.subtask((query, )) for query in queries).apply_async()
    tasks = []
    for result in results:
        refresh_url = result[0] # We need to remember this, and feed it in on a re-run
        taskset = result[1]
        tasks.extend(taskset.subtasks) 
    while tasks:
        current_task = tasks.pop(0)
        if current_task.ready():
            yield current_task.get()
        else:
            tasks.append(current_task)

if __name__ == '__main__':
    for result in stream(['android','bitcoin']):
        print result
