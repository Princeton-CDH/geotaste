#!/usr/bin/env python3

import os,sys
was = os.getcwd()
here = os.path.abspath(os.path.dirname(__file__))
app_py = os.path.join(here,'app.py')
num_workers = 4
host = '0.0.0.0'
port = 8052

# cmd = f'gunicorn app:server --chdir {here} --workers {num_workers} --bind {host}:{port}'
cmd = f'python3 {app_py}'

os.system(cmd)