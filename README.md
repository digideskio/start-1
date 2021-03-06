# start

[![Travis](https://img.shields.io/travis/aldryncore/start.svg?style=flat-square)](https://travis-ci.org/aldryncore/start)
[![PyPI](https://img.shields.io/pypi/v/start.svg?style=flat-square)](https://pypi.python.org/pypi/start/)

Command to start a single process from a Procfile.

``start`` does shell variable expansion for the command string and starts the
command with ``exec``. This means that the command will be the only thing
running and will receive any signals sent to it directly.

Installation:

```
pip install start
```

Usage:

```
start web
```

assuming there is a ``Procfile`` in the current directory or at the path in
the ``PROCFILE_PATH`` environment variable.

```
web: python manage.py runserver
celery: celery -a myapp
```
