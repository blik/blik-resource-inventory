#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Purpose: Run BlikRI on CherryPy WebServer
Created: 20.05.2013
Author:  Aleksey Bogoslovskyi
"""
import os
import sys
import cherrypy
import django.core.handlers.wsgi as wsgi
from django.conf import settings

sys.path.append("/opt/blik/inventory/web_site")


def main():
    """
    Start WebServer
    """
    daemon = cherrypy.process.plugins.Daemonizer(cherrypy.engine)
    daemon.subscribe()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BlikRI.settings'
    app = wsgi.WSGIHandler()
    cherrypy.config.update(os.path.join("/opt/blik/inventory/conf", 'cherrypy.conf'))
    conf = {'/BlikRI': {'tools.wsgiapp.on': True, 'tools.wsgiapp.app': app},
            '/media': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': settings.MEDIA_URL}}
    cherrypy.tree.graft(app, settings.SITE_HOME)
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    main()