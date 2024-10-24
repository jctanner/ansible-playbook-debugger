#!/usr/bin/env python

import shutil
import unittest.mock as mock

from debug_task_executor import DebugTaskExecutor


# get the bin content
ansible_playbook_path = shutil.which('ansible-playbook')
with open(ansible_playbook_path, 'r') as f:
    pb_script = f.read()

# run bin with patched taskexecutor ...
with mock.patch('ansible.executor.task_executor.TaskExecutor', new=DebugTaskExecutor):
    exec(pb_script)
