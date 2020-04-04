#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paste
import cherrypy
from server import app

from paste.translogger import TransLogger

if __name__ == "__main__":
    app = TransLogger(app, setup_console_handler=True)

    cherrypy.tree.graft(app, '')
    cherrypy.config.update({
        'engine.autoreload_on': False,
        'server.socket_port': 4000,
        'server.socket_host': '0.0.0.0',
        'server.thread_pool': 5,
    })

    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()

