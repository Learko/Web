#!/usr/bin/env python3

import sys

from jinja2 import Environment, FileSystemLoader
from pprint import pprint
from webob import Request, Response


dispatch = {
    '/':                    'index.html',
    '/index.html':          'index.html',
    '/about/aboutme.html':  'about/aboutme.html',
    '/github.css':          'github.css'
}

include = (
    'app.js',
    'react.js',
    'leaflet.js',
    'D3.js',
    'moment.js',
    'math.js',
    'main.css',
    'bootstrap.css',
    'normalize.css'
)

css = filter(lambda s: s.endswith('.css'), include)
js  = filter(lambda s: s.endswith('.js'),  include)

env = Environment(loader = FileSystemLoader('template_static'))


class WsgiTopBottomMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        response = self.app(environ, start_response).decode()
        yield response.encode()


def app(environ, start_response):
    path = environ['PATH_INFO']

    res = b''

    if (path in dispatch):
        template = env.get_template(dispatch[path])

        start_response('200 OK', [('Content-Type', 'text/html')])
        res = (template.render(css=css, js=js)).encode()
    else:
        start_response('404 Not Found', [])

    return res


def request(uri):
    req = Request.blank(uri)
    pprint(req)

    print(req.get_response(app))


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    app = WsgiTopBottomMiddleware(app)

    request('/')
    request('/about/aboute.html')