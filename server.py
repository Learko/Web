#!/usr/bin/env python3

import sys

from functools import lru_cache

from curio import run, spawn, TaskGroup
from curio.socket import *


dispatch = {
    '/':                    'static/index.html',
    '/index.html':          'static/index.html',
    '/about/aboutme.html':  'static/about/aboutme.html',
    '/github.css':          'static/github.css'
}


@lru_cache(maxsize=None, typed=True)
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


async def http_handle(conn, addr, port):
    print(f'Client connected: [{addr}:{port}]')

    async with conn:
        data = await conn.recv(1024)

        method, path, proto = data.decode().partition('\n')[0].split()
        print(f'[{addr}:{port}] >>> {method} {path} {proto}')

        if method == 'GET' and proto.startswith('HTTP/1.'):
            if path in dispatch:
                await conn.sendall(f'{proto} 200 OK\r\n\r\n'
                                   f'{read_file(dispatch[path])}'
                                   .encode())
            else:
                await conn.sendall(f'{proto} 404 Not Found\r\n\r\n'.encode())

    print(f'Connection closed: [{addr}:{port}]')


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    run(http_server, 'localhost', 8000)
