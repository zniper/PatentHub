#!/usr/bin/python
import sys
sys.path.insert(0, "/opt/patent")

from flup.server.fcgi import WSGIServer
from pse import app as application


if __name__ == '__main__':
    WSGIServer(application).run()
