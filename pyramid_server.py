#!/usr/bin/env python3

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config


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

css = list(filter(lambda s: s.endswith('.css'), include))
js  = list(filter(lambda s: s.endswith('.js'),  include))


@view_config(
    route_name='root',
    renderer='template_static/index.html')
def root(request):
    return {'css': css, 'js': js}


@view_config(
    route_name='home',
    renderer='template_static/index.html')
def home(request):
    return {'css': css, 'js': js}


@view_config(
    route_name='about',
    renderer='template_static/about/aboutme.html')
def about(request):
    return {'css': css, 'js': js}


if __name__ == '__main__':
    with Configurator() as config:
        config.include('pyramid_jinja2')
        config.add_jinja2_renderer('.html')

        config.add_route('root', '/')
        config.add_route('home', '/index.html')
        config.add_route('about', '/about/aboutme.html')
        config.scan()

        app = config.make_wsgi_app()

    make_server('localhost', 8000, app).serve_forever()
