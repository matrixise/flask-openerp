#!/usr/bin/env python
"""
    demo.py
    ~~~~~~~

    :copyright: (c) 2011 - Stephane Wirtel <stephane@wirtel.be>
    :license: LGPLv2

"""
from flask import Flask
from flaskext.openerp import OpenERP

class DefaultConfig(object):
    OPENERP_PROTOCOL = 'netrpc'
    OPENERP_HOSTNAME = 'localhost'
    OPENERP_DATABASE = 'openerp'
    OPENERP_DEFAULT_USERNAME = 'admin'
    OPENERP_DEFAULT_PASSWORD = 'admin'
    OPENERP_PORT = 8070

    SECRET_KEY = 'secret_key'

    DEBUG = True

app = Flask(__name__)
app.config.from_object(DefaultConfig())
OpenERP(app)

@app.route('/')
def index():
    proxy = Object(g.openerp_cnx, 'res.users')
    users = proxy.select([], ['name', 'login'])

    return str(users)

app.run()

