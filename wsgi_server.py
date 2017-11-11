#!/usr/bin/env python3

import re
import sys

from functools import lru_cache

from curio import run, spawn, TaskGroup
from curio.socket import *


css_format = '<link rel="stylesheet" href="/static/%s"/>'
js_format  = '<script src="/static/%s"></script>'

html_pattern = r'(?P<doctype>.*?)(?P<html_head><html>\s*?<head>\s*?)(?P<head>.*?)(?P<head_body></head>\s*?<body>\s*?)(?P<body>.*?)(?P<body_html></body>\s*?</html>\s*?)'

dispatch = {
    '/':                    'static/index.html',
    '/index.html':          'static/index.html',
    '/about/aboutme.html':  'static/about/aboutme.html',
    '/github.css':          'static/github.css'
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

css = ''.join(map(lambda s: css_format % s, filter(lambda s: s.endswith('.css'), include)))
js  = ''.join(map(lambda s: js_format  % s, filter(lambda s: s.endswith('.js'),  include)))


def wsgi(read):
    def wrapper(path):
        data = read(path)

        if path.endswith('.html'):
            blocks = re.search(html_pattern, data, re.MULTILINE|re.DOTALL)

            data = blocks['doctype']   + blocks['html_head'] \
                 + blocks['head']      + css                 \
                 + blocks['head_body']                       \
                 + blocks['body']      + js                  \
                 + blocks['body_html']

        return data
    return wrapper



# I decided that in this particular case, would be better to wrap this func.
# But you can do it with `response` function.
# `template_server` is more "sample-like"/exemplary
@lru_cache(maxsize=None, typed=True)
@wsgi
def read_file(path):
    with open(path, 'r') as f:
        return f.read()


async def http_server(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(SOMAXCONN)

    print(f'Server listening at [{host}:{port}]')

    async with sock, TaskGroup() as g:
        while True:
            conn, addr = await sock.accept()
            await g.spawn(http_handle, conn, *addr)

def response(method, path, proto):
    if method == 'GET' and proto.startswith('HTTP/1.'):
        if path in dispatch:
            return (f'{proto} 200 OK\r\n\r\n'
                    f'{read_file(dispatch[path])}')
        else:
            return f'{proto} 404 Not Found\r\n\r\n'


async def http_handle(conn, addr, port):
    print(f'Client connected: [{addr}:{port}]')

    async with conn:
        data = await conn.recv(1024)

        method, path, proto = data.decode().partition('\n')[0].split()
        print(f'[{addr}:{port}] >>> {method} {path} {proto}')

        await conn.sendall(response(method, path, proto).encode())

    print(f'Connection closed: [{addr}:{port}]')


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    run(http_server, 'localhost', 8000)
