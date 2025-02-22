#!/usr/bin/python
import sys
import logging
import os
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/OscarWatchApp/")
sys.path.insert(1, "/var/www/OscarWatchApp/venv/lib/python3.12/site-packages/")
os.environ['TEST'] = 'test'
def application(environ, start_response):
    for key in['TEST']:
        os.environ[key] = environ.get(key, '')
    from OscarWatch import app as _application
    _application.secret_key='secret'
    return _application(environ, start_response)
