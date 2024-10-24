import os
import json
import yaml

from ansible.executor.task_executor import TaskExecutor as OriginalTaskExecutor


def task_to_slug(data):

    play_id = data['play_context']['uuid'].split('-')[-1]
    task_id = data['task']['uuid'].split('-')[-1]

    slug = f"{data['host']}@@{data['task_path']}@@{play_id}@@{task_id}"
    slug = slug.replace('/', '_SLASH_')
    slug = slug.replace('.', '_DOT_')
    slug = slug.replace(':', '_COLON_')

    return slug


def get_slug_path(slug):
    slug_file = os.path.join('.data', slug + '.json')
    return slug_file


def serialize_task_executor(task, result):
    pc = task._play_context.serialize()
    for k,v in pc.items():
        if isinstance(v, set):
            pc[k] = list(v)

    ds = {
        'play_context': pc,
        #'task_variable_manager_vars': task._variable_manager.get_vars(),
        'host': str(task._host.name),
        'task': task._task.serialize(),
        'task_path': task._task.get_path(),
        'result': result,
    }
    return ds


def store_data(data):
    ddir = '.data'
    if not os.path.exists(ddir):
        os.makedirs(ddir)

    task_slug = task_to_slug(data)
    fn = os.path.join(ddir, task_slug + '.json')

    with open(fn, 'w') as f:
        f.write(json.dumps(data, indent=2, sort_keys=True))


class DebugTaskExecutor(OriginalTaskExecutor):

    def run(self):

        # do we have a cache for this task?
        ds = serialize_task_executor(self, None)

        if 'nocache' not in self._task.tags:
            task_slug = task_to_slug(ds)
            slug_path = get_slug_path(task_slug)
            if os.path.exists(slug_path):
                with open(slug_path, 'r') as f:
                    ds = json.loads(f.read())
                return ds['result']

        result = super().run()
        ds = serialize_task_executor(self, result)
        store_data(ds)
        return result
