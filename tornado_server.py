import os
import sys
import re
tornado_ROOT_PATH = re.search('(.*)\\\\', os.path.abspath(__file__)).group(1)
sys.path.append(tornado_ROOT_PATH + r'\venv\Lib\site-packages')

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from main import app
from tornado.ioloop import IOLoop


if __name__ == '__main__':
    s = HTTPServer(WSGIContainer(app))
    s.bind(80, '0.0.0.0')
    s.start(1)
    IOLoop.instance().start()